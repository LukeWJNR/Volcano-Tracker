"""
Scientific Paper Reader for Volcano Studies

This page allows users to upload and analyze scientific papers related to volcanology,
with a focus on extracting key insights and data from PDF documents.
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import os
import tempfile
from io import StringIO
import base64
import json
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime

# Try to import PDF processing libraries
try:
    import PyPDF2
    pdf_reader_available = True
except ImportError:
    pdf_reader_available = False
    
try:
    import fitz  # PyMuPDF
    pymupdf_available = True
except ImportError:
    pymupdf_available = False

def app():
    st.title("Volcano Scientific Paper Analyzer")
    
    st.markdown("""
    ## Extract insights from scientific papers on volcanoes
    
    Upload PDF files of scientific papers related to volcanology to extract key insights,
    data, and visualizations. This tool helps you analyze research on topics such as:
    
    - Anak Krakatau collapse events
    - Volcanic plumbing systems
    - Eruption mechanisms and dynamics
    - Volcano monitoring techniques
    - Hazard assessment methodologies
    """)
    
    # Check if PDF processing libraries are available
    if not pdf_reader_available and not pymupdf_available:
        st.warning("""
        📚 **PDF processing libraries are not installed.**
        
        To fully use this feature, you'll need to install PyMuPDF for enhanced processing:
        ```
        pip install pymupdf
        ```
        Or PyPDF2 for basic text extraction:
        ```
        pip install PyPDF2
        ```
        """)
    
    # File uploader for PDFs
    uploaded_files = st.file_uploader("Upload scientific papers (PDF format)", 
                                     type=["pdf"], 
                                     accept_multiple_files=True)
    
    if uploaded_files:
        # Create a selection for which file to process if multiple are uploaded
        file_names = [file.name for file in uploaded_files]
        selected_file = st.selectbox("Select a paper to analyze:", file_names)
        
        # Get the selected file object
        selected_file_obj = next(file for file in uploaded_files if file.name == selected_file)
        
        # Process the selected PDF
        with st.spinner(f"Processing {selected_file}..."):
            # Create a temporary file to save the PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_filename = temp_file.name
                temp_file.write(selected_file_obj.getvalue())
            
            try:
                # Try to extract text and images from the PDF
                if pymupdf_available:
                    text, images, metadata = extract_with_pymupdf(temp_filename)
                elif pdf_reader_available:
                    text, images, metadata = extract_with_pypdf2(temp_filename)
                else:
                    st.error("No PDF processing library available. Unable to extract content.")
                    text, images, metadata = "", [], {}
                
                # Remove the temporary file
                os.unlink(temp_filename)
                
                # Display the extracted content
                display_extracted_content(text, images, metadata, selected_file)
                
                # Analyze the text for volcano-related content
                analyze_volcano_content(text, selected_file)
            
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
                # Remove the temporary file in case of error
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
    
    # Display sample papers if no uploads
    else:
        st.subheader("Sample Volcano Research Papers")
        
        # Create a placeholder for when no papers are uploaded
        st.markdown("""
        ### Ready to analyze scientific papers on:
        
        - **Anak Krakatau Collapse**: Studies on the 2018 flank collapse and tsunami
        - **Volcanic Plumbing Systems**: Research on magma transport and storage
        - **Eruption Dynamics**: Papers on eruption mechanisms and processes
        - **Volcano Monitoring**: Advanced methods for volcano surveillance
        - **Hazard Assessment**: Approaches to evaluate volcanic risks
        
        ⬆️ Upload PDFs above to begin analysis
        """)
        
        # Check for sample PDFs in the attached_assets folder
        sample_papers = []
        
        try:
            import glob
            sample_pdf_paths = glob.glob("attached_assets/*.pdf")
            
            if sample_pdf_paths:
                st.success(f"Found {len(sample_pdf_paths)} sample volcano research papers in the attached_assets folder.")
                
                selected_sample = st.selectbox(
                    "Select a sample paper to analyze:",
                    [os.path.basename(path) for path in sample_pdf_paths]
                )
                
                if selected_sample:
                    selected_path = next(path for path in sample_pdf_paths if os.path.basename(path) == selected_sample)
                    
                    if st.button(f"Analyze {selected_sample}"):
                        with st.spinner(f"Processing {selected_sample}..."):
                            # Process the selected PDF
                            try:
                                # Try to extract text and images from the PDF
                                if pymupdf_available:
                                    text, images, metadata = extract_with_pymupdf(selected_path)
                                elif pdf_reader_available:
                                    text, images, metadata = extract_with_pypdf2(selected_path)
                                else:
                                    st.error("No PDF processing library available. Unable to extract content.")
                                    text, images, metadata = "", [], {}
                                
                                # Display the extracted content
                                display_extracted_content(text, images, metadata, selected_sample)
                                
                                # Analyze the text for volcano-related content
                                analyze_volcano_content(text, selected_sample)
                            except Exception as e:
                                st.error(f"Error processing PDF: {str(e)}")
                    
                    # Also provide info about analyzing your own PDFs
                    st.info("You can also upload your own volcano research papers using the file uploader above.")
                
        except Exception as e:
            st.warning(f"Could not access sample papers: {str(e)}")
        
        # Display a list of notable papers in the field as examples
        with st.expander("Notable Papers in Volcanology"):
            papers = [
                {
                    "title": "Complex hazard cascade culminating in the Anak Krakatau sector collapse",
                    "authors": "Walter, T.R., et al.",
                    "journal": "Nature Communications",
                    "year": 2019,
                    "doi": "10.1038/s41467-019-12284-5",
                    "abstract": "The 22 Dec 2018 flank collapse of Anak Krakatau volcano led to a tsunami on the coasts of Sumatra and Java. This study examines the complex cascade of events and implications for hazard assessment."
                },
                {
                    "title": "Magma reservoirs under Yellowstone: new views from seismic tomography and deformation modeling",
                    "authors": "Huang, H.H., et al.",
                    "journal": "Science",
                    "year": 2015,
                    "doi": "10.1126/science.aaa5648",
                    "abstract": "This study provides new insights into the magmatic system beneath Yellowstone, revealing a continuous vertical zone of low-velocity material rising from the mantle plume to the magma reservoir."
                },
                {
                    "title": "Studying Volcanic Plumbing Systems – Multidisciplinary Approaches to a Multifaceted Problem",
                    "authors": "Burchardt, S. and Galland, O.",
                    "journal": "Geological Society Special Publications",
                    "year": 2016,
                    "doi": "10.1144/SP234.1",
                    "abstract": "This review paper discusses the current state of knowledge about volcanic plumbing systems, emphasizing the need for multidisciplinary approaches to understand these complex structures."
                }
            ]
            
            for paper in papers:
                st.markdown(f"""
                **{paper['title']}**  
                {paper['authors']}  
                *{paper['journal']}* ({paper['year']})  
                DOI: {paper['doi']}
                
                {paper['abstract']}
                
                ---
                """)
    
    # Provide some volcano-related research categories
    st.sidebar.header("Research Categories")
    categories = [
        "Volcanic Plumbing Systems",
        "Eruption Mechanisms",
        "Volcano Monitoring",
        "Hazard Assessment",
        "Historical Eruptions",
        "Volcanic Landforms",
        "Magma Composition",
        "Case Studies",
        "Volcanic Tsunamis"
    ]
    
    selected_categories = st.sidebar.multiselect("Filter by research focus:", categories)
    
    # Links to volcano research resources
    st.sidebar.header("Research Resources")
    st.sidebar.markdown("""
    - [Journal of Volcanology and Geothermal Research](https://www.journals.elsevier.com/journal-of-volcanology-and-geothermal-research)
    - [Bulletin of Volcanology](https://www.springer.com/journal/445)
    - [Global Volcanism Program](https://volcano.si.edu/)
    - [USGS Volcano Hazards Program](https://www.usgs.gov/volcano)
    - [Smithsonian Volcanism Archive](https://volcano.si.edu/search_volcano.cfm)
    """)
    
    # Add example citation format
    st.sidebar.header("Cite Papers In Dashboard")
    st.sidebar.markdown("""
    Format citations as:  
    
    ```
    Author(s) (Year). Title. Journal, Volume(Issue), Pages.
    ```
    
    Example:  
    ```
    Walter, T.R., et al. (2019). Complex hazard cascade culminating in the Anak Krakatau sector collapse. Nature Communications, 10, 4339.
    ```
    """)


def extract_with_pymupdf(filepath):
    """Extract text, images and metadata from PDF using PyMuPDF."""
    doc = fitz.open(filepath)
    
    # Extract metadata
    metadata = {
        'title': doc.metadata.get('title', 'Unknown'),
        'author': doc.metadata.get('author', 'Unknown'),
        'subject': doc.metadata.get('subject', ''),
        'keywords': doc.metadata.get('keywords', ''),
        'creator': doc.metadata.get('creator', ''),
        'producer': doc.metadata.get('producer', ''),
        'page_count': len(doc),
        'creation_date': doc.metadata.get('creationDate', '')
    }
    
    # Extract text
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    
    # Extract images
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Get images
        image_list = page.get_images(full=True)
        
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(image_bytes))
                
                # Add image to list with metadata
                images.append({
                    'page': page_num + 1,
                    'index': img_index,
                    'width': image.width,
                    'height': image.height,
                    'image': image
                })
            except Exception as e:
                print(f"Error extracting image: {e}")
    
    doc.close()
    return text, images, metadata


def extract_with_pypdf2(filepath):
    """Extract text and limited metadata from PDF using PyPDF2 (fallback method)."""
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Extract metadata
        info = reader.metadata
        metadata = {
            'title': info.get('/Title', 'Unknown') if info else 'Unknown',
            'author': info.get('/Author', 'Unknown') if info else 'Unknown',
            'subject': info.get('/Subject', '') if info else '',
            'keywords': info.get('/Keywords', '') if info else '',
            'creator': info.get('/Creator', '') if info else '',
            'producer': info.get('/Producer', '') if info else '',
            'page_count': len(reader.pages),
            'creation_date': info.get('/CreationDate', '') if info else ''
        }
        
        # Extract text
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    
    # PyPDF2 doesn't extract images easily
    images = []
    
    return text, images, metadata


def display_extracted_content(text, images, metadata, filename):
    """Display the extracted content from the PDF."""
    # Display paper metadata
    st.subheader("Paper Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Title:** {metadata.get('title', 'Unknown')}")
        st.markdown(f"**Author(s):** {metadata.get('author', 'Unknown')}")
        st.markdown(f"**Keywords:** {metadata.get('keywords', 'None')}")
    
    with col2:
        st.markdown(f"**Pages:** {metadata.get('page_count', 0)}")
        st.markdown(f"**Created with:** {metadata.get('creator', 'Unknown')}")
        creation_date = metadata.get('creation_date', '')
        if creation_date:
            st.markdown(f"**Created on:** {creation_date}")
    
    # Allow downloading the extracted text
    text_download = st.download_button(
        label="Download Extracted Text",
        data=text,
        file_name=f"{os.path.splitext(filename)[0]}_extracted.txt",
        mime="text/plain"
    )
    
    # Display abstract if it can be identified
    abstract = extract_abstract(text)
    if abstract:
        st.subheader("Abstract")
        st.markdown(abstract)
    
    # Display extracted images
    if images:
        st.subheader(f"Extracted Figures ({len(images)})")
        
        image_cols = st.columns(3)
        for i, img_data in enumerate(images):
            with image_cols[i % 3]:
                st.image(img_data['image'], caption=f"Figure from page {img_data['page']}", use_container_width=True)
                
                # If we have PyMuPDF, provide option to download images
                if pymupdf_available:
                    img_byte_arr = io.BytesIO()
                    img_data['image'].save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    st.download_button(
                        label=f"Download Figure {i+1}",
                        data=img_byte_arr,
                        file_name=f"figure_{i+1}_page_{img_data['page']}.png",
                        mime="image/png"
                    )
    
    # Display a preview of the extracted text
    with st.expander("Text Preview (first 5000 characters)"):
        st.text(text[:5000] + "..." if len(text) > 5000 else text)


def extract_abstract(text):
    """
    Attempt to extract the abstract from the paper text.
    This is heuristic-based and may not work for all papers.
    """
    # Method 1: Look for section labeled as abstract
    abstract_pattern = re.compile(r'(?i)abstract\s*\n*(.+?)(?:\n\s*(?:introduction|keywords|1\.)|$)', re.DOTALL)
    match = abstract_pattern.search(text)
    
    if match:
        abstract = match.group(1).strip()
        # Clean up the abstract (remove excessive whitespace, etc.)
        abstract = re.sub(r'\s+', ' ', abstract)
        return abstract
    
    # Method 2: Try to find the first substantial paragraph after the title/authors
    # This is less reliable but can work for some papers
    paragraphs = re.split(r'\n\s*\n', text[:3000])  # Look only in first 3000 chars
    
    # Skip very short paragraphs and find the first substantial one
    for para in paragraphs:
        cleaned_para = para.strip()
        word_count = len(re.findall(r'\b\w+\b', cleaned_para))
        
        if word_count > 30 and len(cleaned_para) > 200:
            return cleaned_para
    
    return None


def analyze_volcano_content(text, filename):
    """Analyze the text for volcano-related content and extract key insights."""
    st.subheader("Volcano Content Analysis")
    
    # Check if the paper is about volcanoes
    if not is_volcano_paper(text):
        st.warning("This paper may not be primarily focused on volcanology. Analysis may be limited.")
    
    # Extract key volcano-related terms and their contexts
    volcano_terms = extract_volcano_terms(text)
    
    if volcano_terms:
        # Display the most frequently mentioned volcano terms
        term_counts = {term: count for term, count, _ in volcano_terms[:10]}
        
        # Create a bar chart of term frequency
        fig, ax = plt.subplots(figsize=(10, 5))
        terms = list(term_counts.keys())
        counts = list(term_counts.values())
        
        # Sort by frequency
        sorted_indices = np.argsort(counts)
        terms = [terms[i] for i in sorted_indices]
        counts = [counts[i] for i in sorted_indices]
        
        y_pos = range(len(terms))
        ax.barh(y_pos, counts, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(terms)
        ax.invert_yaxis()  # Labels read top-to-bottom
        ax.set_xlabel('Frequency')
        ax.set_title('Key Volcanic Terms Mentioned')
        
        st.pyplot(fig)
        
        # Show contexts for the top terms
        st.subheader("Key Volcanic Terms in Context")
        
        for term, count, contexts in volcano_terms[:5]:
            with st.expander(f"{term} (mentioned {count} times)"):
                for context in contexts[:3]:  # Show up to 3 contexts per term
                    st.markdown(f"...**{context}**...")
        
        # Attempt to identify specific volcanoes mentioned
        volcanoes = identify_volcanoes(text)
        if volcanoes:
            st.subheader("Specific Volcanoes Mentioned")
            
            # Create a dataframe for the volcanoes
            volcano_df = pd.DataFrame({
                'Volcano': [v[0] for v in volcanoes],
                'Mentions': [v[1] for v in volcanoes]
            })
            
            # Display as a table
            st.table(volcano_df)
    
    # Extract numerical data if present
    with st.expander("Attempt to Extract Numerical Data"):
        extract_numerical_data(text)
    
    # Create tagged version of the text
    with st.expander("View Tagged Text"):
        st.markdown("The original text with volcanic terms highlighted:")
        tagged_text = create_tagged_text(text, [term for term, _, _ in volcano_terms])
        st.markdown(tagged_text[:10000] + "..." if len(tagged_text) > 10000 else tagged_text, unsafe_allow_html=True)


def is_volcano_paper(text):
    """Determine if the paper is primarily about volcanoes."""
    # List of key volcanological terms
    volcano_terms = [
        'volcano', 'volcanic', 'eruption', 'magma', 'lava', 'pyroclastic',
        'caldera', 'tephra', 'ash', 'lahar', 'stratovolcano', 'shield volcano'
    ]
    
    # Check frequency of these terms
    text_lower = text.lower()
    term_counts = {term: text_lower.count(term) for term in volcano_terms}
    total_count = sum(term_counts.values())
    
    # Heuristic: If these terms appear more than 20 times, it's likely a volcano paper
    return total_count > 20


def extract_volcano_terms(text):
    """Extract volcano-related terms and their context from the text."""
    # Comprehensive list of volcano-related terms
    volcano_terms = [
        'volcano', 'volcanic', 'eruption', 'magma', 'lava', 'pyroclastic',
        'caldera', 'tephra', 'ash', 'lahar', 'stratovolcano', 'shield volcano',
        'cinder cone', 'vent', 'fissure', 'dyke', 'dike', 'sill', 'intrusion',
        'extrusion', 'pluton', 'chamber', 'reservoir', 'plumbing', 'feeding system',
        'conduit', 'dome', 'crater', 'flank', 'collapse', 'landslide', 'sector collapse',
        'debris avalanche', 'tsunami', 'plinian', 'strombolian', 'vulcanian', 'subplinian',
        'hawaiian', 'phreatic', 'phreatomagmatic', 'effusive', 'explosive',
        'pumice', 'scoria', 'obsidian', 'rhyolite', 'andesite', 'basalt', 'dacite',
        'fumarole', 'geyser', 'hydrothermal', 'monitoring', 'deformation', 'seismicity',
        'gas emission', 'infrasound', 'InSAR', 'tomography', 'geophysical', 'geochemical',
        'magmatic', 'viscosity', 'crystallization', 'degassing', 'fragmentation',
        'eruptive column', 'plume', 'hazard', 'risk', 'alert level', 'evacuation'
    ]
    
    # Find occurrences of terms with context
    text_lower = text.lower()
    term_contexts = []
    
    for term in volcano_terms:
        # Find all occurrences of the term
        count = text_lower.count(term)
        
        if count > 0:
            # Extract contexts (30 chars before and after)
            contexts = []
            for match in re.finditer(r'\b' + re.escape(term) + r'\b', text_lower):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end].replace('\n', ' ').strip()
                contexts.append(context)
            
            term_contexts.append((term, count, contexts))
    
    # Sort by frequency (most frequent first)
    term_contexts.sort(key=lambda x: x[1], reverse=True)
    
    return term_contexts


def identify_volcanoes(text):
    """Identify specific volcanoes mentioned in the text."""
    # List of notable volcanoes worldwide
    notable_volcanoes = [
        'Anak Krakatau', 'Krakatau', 'Krakatoa', 'Vesuvius', 'Etna', 'Stromboli',
        'Yellowstone', 'Kilauea', 'Mauna Loa', 'Fuji', 'St. Helens', 'Mount St. Helens',
        'Pinatubo', 'Tambora', 'Merapi', 'Eyjafjallajökull', 'Katla',
        'Ruapehu', 'Taupo', 'Taal', 'Popocatépetl', 'Cotopaxi', 'Tungurahua',
        'Villarrica', 'Nevado del Ruiz', 'Galeras', 'Santorini', 'Erebus',
        'Nyiragongo', 'Ol Doinyo Lengai', 'Soufrière Hills', 'Long Valley',
        'Unzen', 'Sakurajima', 'Ontake', 'Kelud', 'Sinabung', 'Agung',
        'Klyuchevskoy', 'Elbrus', 'Teide', 'Cumbre Vieja', 'Hekla', 'Grímsvötn'
    ]
    
    # Find occurrences of volcano names
    text_lower = text.lower()
    volcano_counts = []
    
    for volcano in notable_volcanoes:
        volcano_lower = volcano.lower()
        count = text_lower.count(volcano_lower)
        
        if count > 0:
            volcano_counts.append((volcano, count))
    
    # Sort by frequency (most frequent first)
    volcano_counts.sort(key=lambda x: x[1], reverse=True)
    
    return volcano_counts


def extract_numerical_data(text):
    """
    Attempt to extract numerical data and tables from the text.
    This is a simplified approach and may not work well for all papers.
    """
    # Pattern for numbers with units commonly found in volcanology
    patterns = [
        # Volume measurements
        r'(\d+(?:\.\d+)?)\s*(?:km3|cubic kilometers?|km³)',
        # Height/depth measurements
        r'(\d+(?:\.\d+)?)\s*(?:m|km|meters?|kilometres?)',
        # Temperature
        r'(\d+(?:\.\d+)?)\s*(?:°C|degrees C|degrees Celsius)',
        # Time durations
        r'(\d+(?:\.\d+)?)\s*(?:hours?|days?|weeks?|months?|years?)',
        # Percentages
        r'(\d+(?:\.\d+)?)\s*%',
        # Dates
        r'\b(\d{1,2}(?:\s*[-./]\s*\d{1,2}){1,2}(?:\s*[-./]\s*\d{2,4})?)\b'
    ]
    
    # Extract data
    extracted_data = []
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            extracted_data.append(match.group(0))
    
    # Display extracted data
    if extracted_data:
        st.markdown("### Extracted Numerical Values")
        
        # Count unique entries and take top 20
        data_counts = pd.Series(extracted_data).value_counts().head(20)
        
        # Display as a bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        data_counts.plot(kind='barh', ax=ax)
        ax.set_title('Commonly Mentioned Measurements')
        ax.set_xlabel('Frequency')
        st.pyplot(fig)
        
        # Also show as a table
        st.markdown("### Top Measurements Mentioned")
        data_df = pd.DataFrame({
            'Measurement': data_counts.index,
            'Mentions': data_counts.values
        })
        st.table(data_df)
    else:
        st.info("No structured numerical data detected in the standard formats.")
    
    # Look for potential tables
    identify_potential_tables(text)


def identify_potential_tables(text):
    """Try to identify potential tables in the text."""
    # Look for sections with multiple lines containing numbers and consistent spacing
    lines = text.split('\n')
    candidate_table_sections = []
    current_section = []
    in_table = False
    
    for line in lines:
        # Check if the line has numbers and several whitespace separations
        has_numbers = bool(re.search(r'\d', line))
        has_multiple_spaces = len(re.findall(r'\s{2,}', line)) >= 2
        
        if has_numbers and has_multiple_spaces:
            if not in_table:
                in_table = True
            current_section.append(line)
        else:
            if in_table and len(current_section) >= 3:
                candidate_table_sections.append(current_section)
            in_table = False
            current_section = []
    
    # Add the last section if it exists
    if in_table and len(current_section) >= 3:
        candidate_table_sections.append(current_section)
    
    # Display potential tables
    if candidate_table_sections:
        st.markdown("### Potential Tables Detected")
        
        for i, section in enumerate(candidate_table_sections[:3]):  # Show up to 3 potential tables
            with st.expander(f"Potential Table {i+1}"):
                st.text('\n'.join(section))
                
                # Try to parse into a dataframe (very simplistic approach)
                try:
                    # Try to create a CSV-like string
                    csv_like = '\n'.join(line.strip() for line in section)
                    
                    # Replace multiple spaces with a single comma
                    csv_like = re.sub(r'\s{2,}', ',', csv_like)
                    
                    # Try to parse with pandas
                    df = pd.read_csv(StringIO(csv_like), header=None)
                    
                    st.markdown("#### Attempted Table Parsing:")
                    st.dataframe(df)
                except Exception as e:
                    st.warning(f"Could not automatically parse into table format: {str(e)}")
    else:
        st.info("No clear tabular data detected in the text.")


def create_tagged_text(text, terms):
    """Create a version of the text with volcano terms highlighted."""
    # Replace newlines with <br> for HTML display
    html_text = text.replace('\n', '<br>')
    
    # Highlight terms
    for term in terms:
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        html_text = pattern.sub(f'<span style="background-color: #ffeb9a; font-weight: bold;">{term}</span>', html_text)
    
    return html_text


if __name__ == "__main__":
    app()