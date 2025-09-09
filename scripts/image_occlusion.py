#!/usr/bin/env python3
"""
Image Occlusion Card Generator for Anki
Creates cards by generating HTML/SVG masks for image regions.
"""

import sys
import argparse
import json
import csv
from typing import List, Tuple, Dict, Optional
from anki_utils import AnkiWriter, create_argument_parser


class ImageOcclusionGenerator:
    """Generate image occlusion cards for Anki."""
    
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.regions = []
        self.cards = []
    
    def add_region(self, x: int, y: int, width: int, height: int, 
                   label: str, hint: Optional[str] = None):
        """Add a region to occlude.
        
        Args:
            x, y: Top-left coordinates of the region
            width, height: Dimensions of the region
            label: The text revealed when studying
            hint: Optional hint shown on the occluded region
        """
        self.regions.append({
            'x': x, 'y': y,
            'width': width, 'height': height,
            'label': label,
            'hint': hint
        })
    
    def generate_svg_mask(self, hide_indices: List[int], 
                         show_hints: bool = True) -> str:
        """Generate SVG overlay for specified regions.
        
        Args:
            hide_indices: Indices of regions to hide
            show_hints: Whether to show hint text on hidden regions
        """
        svg_parts = []
        
        for i, region in enumerate(self.regions):
            if i in hide_indices:
                # Create rectangle mask
                svg_parts.append(
                    f'<rect x="{region["x"]}" y="{region["y"]}" '
                    f'width="{region["width"]}" height="{region["height"]}" '
                    f'fill="yellow" opacity="0.9" stroke="red" stroke-width="2"/>'
                )
                
                # Add hint text if provided
                if show_hints and region['hint']:
                    text_x = region['x'] + region['width'] // 2
                    text_y = region['y'] + region['height'] // 2
                    svg_parts.append(
                        f'<text x="{text_x}" y="{text_y}" '
                        f'text-anchor="middle" dominant-baseline="middle" '
                        f'font-size="14" fill="black">{region["hint"]}</text>'
                    )
        
        return '\n'.join(svg_parts)
    
    def generate_html_card(self, hide_indices: List[int], 
                          question: str = "Identify the highlighted regions") -> Tuple[str, str]:
        """Generate HTML for front and back of card.
        
        Args:
            hide_indices: Indices of regions to hide
            question: Question text for the card
        
        Returns:
            Tuple of (front_html, back_html)
        """
        # Front of card - with occlusions
        front_svg = self.generate_svg_mask(hide_indices, show_hints=True)
        front_html = f'''
<div style="position: relative; display: inline-block;">
    <img src="{self.image_path}" style="max-width: 100%;">
    <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
        {front_svg}
    </svg>
</div>
<br><br>
<b>{question}</b>
        '''.strip()
        
        # Back of card - show labels for hidden regions
        back_parts = []
        for i in hide_indices:
            region = self.regions[i]
            back_parts.append(f"• {region['label']}")
        
        back_svg = self.generate_svg_mask(hide_indices, show_hints=False)
        # Highlight revealed regions in green
        for i in hide_indices:
            region = self.regions[i]
            back_svg += f'''
<rect x="{region['x']}" y="{region['y']}" 
      width="{region['width']}" height="{region['height']}" 
      fill="none" stroke="green" stroke-width="3"/>
<text x="{region['x'] + region['width']//2}" 
      y="{region['y'] + region['height']//2}" 
      text-anchor="middle" dominant-baseline="middle" 
      font-size="16" fill="green" font-weight="bold">{region['label']}</text>
            '''
        
        back_html = f'''
<div style="position: relative; display: inline-block;">
    <img src="{self.image_path}" style="max-width: 100%;">
    <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
        {back_svg}
    </svg>
</div>
<br><br>
<b>Answers:</b><br>
{'<br>'.join(back_parts)}
        '''.strip()
        
        return (front_html, back_html)
    
    def generate_individual_cards(self) -> List[Tuple[str, str]]:
        """Generate one card per region."""
        cards = []
        
        for i, region in enumerate(self.regions):
            question = f"What is this part of the image?"
            if region['hint']:
                question = f"Identify: {region['hint']}"
            
            front, back = self.generate_html_card([i], question)
            cards.append((front, back))
        
        return cards
    
    def generate_group_cards(self, groups: List[List[int]]) -> List[Tuple[str, str]]:
        """Generate cards for groups of regions.
        
        Args:
            groups: List of lists, each containing indices to hide together
        """
        cards = []
        
        for group in groups:
            if group:  # Skip empty groups
                labels = [self.regions[i]['label'] for i in group]
                question = f"Identify these {len(group)} regions"
                
                front, back = self.generate_html_card(group, question)
                cards.append((front, back))
        
        return cards
    
    def generate_all_cards(self, mode: str = 'individual') -> List[Tuple[str, str]]:
        """Generate cards based on mode.
        
        Args:
            mode: 'individual', 'all', or 'progressive'
        """
        if mode == 'individual':
            return self.generate_individual_cards()
        elif mode == 'all':
            # One card with all regions hidden
            all_indices = list(range(len(self.regions)))
            front, back = self.generate_html_card(all_indices, 
                                                 "Identify all labeled regions")
            return [(front, back)]
        elif mode == 'progressive':
            # Progressive reveal - hide more regions each time
            cards = []
            for i in range(1, len(self.regions) + 1):
                indices = list(range(i))
                question = f"Identify the first {i} region(s)"
                front, back = self.generate_html_card(indices, question)
                cards.append((front, back))
            return cards
        else:
            return []


def parse_regions_file(filepath: str) -> List[Dict]:
    """Parse a JSON file containing region definitions."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Validate required fields
    required = ['x', 'y', 'width', 'height', 'label']
    regions = []
    
    for region in data.get('regions', []):
        if all(field in region for field in required):
            regions.append(region)
    
    return regions


def main():
    parser = argparse.ArgumentParser(
        description='Generate image occlusion cards for Anki',
        epilog='''
Example regions.json format:
{
  "image": "anatomy.png",
  "regions": [
    {"x": 100, "y": 50, "width": 80, "height": 60, 
     "label": "Heart", "hint": "Pumps blood"},
    {"x": 200, "y": 150, "width": 70, "height": 50, 
     "label": "Lung", "hint": "Gas exchange"}
  ]
}
        '''
    )
    
    parser.add_argument(
        'image', help='Path to the image file'
    )
    parser.add_argument(
        '-r', '--regions', type=str, required=True,
        help='JSON file containing region definitions'
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), 
        default=sys.stdout,
        help='Output CSV file (default: stdout)'
    )
    parser.add_argument(
        '-m', '--mode', 
        choices=['individual', 'all', 'progressive', 'groups'],
        default='individual',
        help='Card generation mode'
    )
    parser.add_argument(
        '--groups', type=str,
        help='JSON file with custom groupings for group mode'
    )
    
    args = parser.parse_args()
    
    # Parse regions
    regions_data = parse_regions_file(args.regions)
    
    # Create generator
    generator = ImageOcclusionGenerator(args.image)
    
    # Add regions
    for region in regions_data:
        generator.add_region(
            region['x'], region['y'],
            region['width'], region['height'],
            region['label'],
            region.get('hint')
        )
    
    # Generate cards based on mode
    if args.mode == 'groups' and args.groups:
        with open(args.groups, 'r') as f:
            groups = json.load(f)['groups']
        cards = generator.generate_group_cards(groups)
    else:
        cards = generator.generate_all_cards(args.mode)
    
    # Write output
    AnkiWriter.write_csv(cards, args.output)
    
    if args.output != sys.stdout:
        print(f"Generated {len(cards)} image occlusion cards", file=sys.stderr)


if __name__ == '__main__':
    main()