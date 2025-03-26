import os
import csv
import re
from PyPDF2 import PdfReader
import textwrap

def clean_string(input_string: str) -> str:
    return re.sub(r'[^a-zA-Z0-9 \n\t]', '', input_string)

def smart_section_split(text):
    """Splits paragraphs using sentence-ending punctuation and line breaks."""
    return re.split(r'(?<=[.;_])\s*\n', text)  # Split at periods followed by newlines

def extract_paragraphs_from_pdfs(pdf_folder, output_csv, max_lines_per_paragraph=500):
    """
    Extract paragraphs from PDF files and write them to a CSV file.
    
    Args:
        pdf_folder (str): Folder containing the PDF files
        output_csv (str): Path to the output CSV file
        max_lines_per_paragraph (int): Maximum lines a paragraph can have before being split
    """
    # Check if the PDF folder exists
    if not os.path.exists(pdf_folder):
        print(f"Error: The folder '{pdf_folder}' does not exist.")
        return
    
    # Get all PDF files in the folder
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{pdf_folder}'.")
        return
    
    # Create CSV file and write header
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['PDF File', 'Page Number', 'Paragraph'])
        
        # Process each PDF file
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_folder, pdf_file)
            print(f"Processing: {pdf_file}")
            
            try:
                # Open the PDF
                pdf_reader = PdfReader(pdf_path)
                
                # Process each page
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    
                    if not text:
                        continue
                    
                    # Split the text into paragraphs
                    # We'll consider text separated by double newlines as paragraphs
                    # raw_paragraphs = re.split(r'\n\s*\n', text)
                    raw_paragraphs = smart_section_split(text)
                    for raw_paragraph in raw_paragraphs:
                        paragraph = raw_paragraph.strip()
                        lines = paragraph.split('\n')
                        joined_paragraph = ' '.join([line.strip() for line in lines])
                        # further clean by removing special chars
                        clean_paragraph = clean_string(joined_paragraph)
                        # If the paragraph exceeds max_lines_per_paragraph, split it
                        if len(lines) > max_lines_per_paragraph:
                            # Estimate characters per line
                            avg_chars_per_line = sum(len(line) for line in lines) // len(lines)
                            max_chars = avg_chars_per_line * max_lines_per_paragraph
                            
                            # Split the paragraph into chunks of approximately max_lines_per_paragraph
                            chunks = textwrap.wrap(clean_paragraph, width=max_chars)
                            
                            for chunk in chunks:
                                if len(chunk.split()) > 10:  # Only include substantive chunks
                                    csv_writer.writerow([pdf_file, page_num, chunk])
                        else:
                            # Write the original paragraph if it's not too long
                            if len(clean_paragraph.split()) > 10:  # Only include substantive paragraphs
                                csv_writer.writerow([pdf_file, page_num, clean_paragraph])
            
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
                # Continue with the next PDF
    
    print(f"Extraction complete. Results saved to {output_csv}")

def main():
    pdf_folder = "bank_guarantee_pdfs"  # The folder where PDFs were downloaded
    output_csv = "./pdf-tools/bank_guarantee_paragraphs.csv"
    max_lines = 12  # Maximum number of lines per paragraph
    
    extract_paragraphs_from_pdfs(pdf_folder, output_csv, max_lines)

if __name__ == "__main__":
    main()