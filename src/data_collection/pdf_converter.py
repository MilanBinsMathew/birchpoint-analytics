import os
from pdf2image import convert_from_path
from PIL import Image
import logging
from typing import List, Dict, Any
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFConverter:
    def __init__(self, dpi: int = 300, output_format: str = 'PNG'):
        self.dpi = dpi
        self.output_format = output_format

    def convert_pdf_to_images(
        self,
        pdf_path: str,
        output_dir: str,
        metadata: Dict[str, Any] = None
    ) -> List[str]:
        try:
            logger.info(f"Converting PDF: {pdf_path}")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=self.dpi)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            image_paths = []
            for i, image in enumerate(images):
                # Generate filename
                image_filename = f"page_{i+1:03d}.{self.output_format.lower()}"
                image_path = os.path.join(output_dir, image_filename)
                
                # Save image
                image.save(image_path, self.output_format)
                image_paths.append(image_path)
            
            # Save metadata
            if metadata:
                metadata_path = os.path.join(output_dir, 'metadata.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            logger.info(f"Converted {len(images)} pages to images")
            return image_paths
            
        except Exception as e:
            logger.error(f"Failed to convert PDF {pdf_path}: {e}")
            return []

    def convert_all_pdfs_in_directory(
        self,
        base_dir: str = "./data/companies",
        metadata_base: Dict[str, Any] = None
    ) -> Dict[str, List[str]]:
        results = {}
        
        for company_dir in os.listdir(base_dir):
            company_path = os.path.join(base_dir, company_dir)
            
            if not os.path.isdir(company_path):
                continue
            
            logger.info(f"Processing company: {company_dir}")
            
            # Create images directory
            images_dir = os.path.join(company_path, 'images')
            os.makedirs(images_dir, exist_ok=True)
            
            # Find all PDFs
            pdf_files = [f for f in os.listdir(company_path) if f.endswith('.pdf')]
            
            company_results = []
            for pdf_file in pdf_files:
                pdf_path = os.path.join(company_path, pdf_file)
                
                # Create subdirectory for this PDF
                pdf_name = os.path.splitext(pdf_file)[0]
                pdf_images_dir = os.path.join(images_dir, pdf_name)
                
                # Prepare metadata
                pdf_metadata = {
                    'company': company_dir,
                    'pdf_file': pdf_file,
                    **(metadata_base or {})
                }
                
                # Convert
                image_paths = self.convert_pdf_to_images(
                    pdf_path,
                    pdf_images_dir,
                    pdf_metadata
                )
                
                company_results.extend(image_paths)
            
            results[company_dir] = company_results
        
        return results

    def create_image_manifest(
        self,
        base_dir: str = "./data/companies",
        output_path: str = "./data/image_manifest.json"
    ):
        manifest = []
        
        for company_dir in os.listdir(base_dir):
            company_path = os.path.join(base_dir, company_dir)
            images_dir = os.path.join(company_path, 'images')
            
            if not os.path.isdir(images_dir):
                continue
            
            for pdf_dir in os.listdir(images_dir):
                pdf_path = os.path.join(images_dir, pdf_dir)
                metadata_path = os.path.join(pdf_path, 'metadata.json')
                
                # Load metadata if exists
                metadata = {}
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                
                # Add image entries
                for image_file in os.listdir(pdf_path):
                    if image_file.endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(pdf_path, image_file)
                        page_num = int(image_file.split('_')[1].split('.')[0])
                        
                        manifest.append({
                            'image_path': image_path,
                            'company': company_dir,
                            'pdf_name': pdf_dir,
                            'page_number': page_num,
                            'metadata': metadata
                        })
        
        # Save manifest
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Created image manifest with {len(manifest)} entries")
        return manifest


if __name__ == "__main__":
    converter = PDFConverter()
    results = converter.convert_all_pdfs_in_directory()
    converter.create_image_manifest()
