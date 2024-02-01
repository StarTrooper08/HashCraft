import os
import requests
from pyhtml2pdf import converter
import re
import subprocess

def fetch_html_content():
    url = "https://gql.hashnode.com/"

    query = """
    query Publication {
      publication(host: "atharva08.hashnode.dev") {
        post(slug: "efficiency-unleashed-dockerizing-and-optimizing-a-fastapi-app-with-slimtoolkit-and-github-actions") {
          title
          content {
            html
          }
          author {
            name
          }
        }
      }
    }
    """

    data = {"query": query}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()
        title = result["data"]["publication"]["post"]["title"]
        author_name = result["data"]["publication"]["post"]["author"]["name"]
        html_content = result["data"]["publication"]["post"]["content"]["html"]
        return title, author_name, html_content
    else:
        print(f"GraphQL request failed with status code {response.status_code}: {response.text}")
        return None, None, None

def remove_emojis(html_content):
    emoji_pattern = re.compile("["
                               "\U0001F600-\U0001F64F"
                               "\U0001F300-\U0001F5FF"
                               "\U0001F680-\U0001F6FF"
                               "\U0001F700-\U0001F77F"
                               "\U0001F780-\U0001F7FF"
                               "\U0001F800-\U0001F8FF"
                               "\U0001F900-\U0001F9FF"
                               "\U0001FA00-\U0001FA6F"
                               "\U0001FA70-\U0001FAFF"
                               "\U00002702-\U000027B0"
                               "\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    cleaned_html = emoji_pattern.sub('', html_content)
    return cleaned_html

def create_html_file(html_content):
    html_filename = "output.html"
    with open(html_filename, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
    return html_filename

def convert_html_to_pdf(title, author_name, html_filename, pdf_filename):
    # Use the title as header in the PDF
    header_html = f"<h1>{title}</h1>"

    # Combine the header HTML and the existing HTML content
    full_html = header_html + open(html_filename, "r", encoding="utf-8").read()

    # Add footer only on the last page
    footer_html = f'<div style="text-align: center; margin-top: 20px;">Hashnode / {author_name}</div>'
    full_html += footer_html

    # Save the combined HTML to a temporary file
    temp_html_filename = "temp_output.html"
    with open(temp_html_filename, "w", encoding="utf-8") as temp_html_file:
        temp_html_file.write(full_html)

    # Convert the combined HTML to PDF
    converter.convert(f'file:///{os.path.abspath(temp_html_filename)}', pdf_filename)

    # Remove the temporary HTML file
    os.remove(temp_html_filename)

def convert_html_to_epub(title, html_filename, epub_filename):
    # Use subprocess to call Pandoc for HTML to EPUB conversion
    subprocess.run(['pandoc', html_filename, '-o', epub_filename, '--metadata', f'title={title}'])

    # Remove the temporary HTML file
    os.remove(html_filename)

if __name__ == "__main__":
    title, author_name, html_content = fetch_html_content()

    if title and author_name and html_content:
        # Remove emojis from the HTML content
        cleaned_html = remove_emojis(html_content)

        # Create and save the cleaned HTML file
        html_filename = create_html_file(cleaned_html)

        # PDF conversion
        pdf_filename = "output.pdf"
        convert_html_to_pdf(title, author_name, html_filename, pdf_filename)
        print(f"PDF generated successfully: {pdf_filename}")

        # EPUB conversion
        epub_filename = "output.epub"
        convert_html_to_epub(title, html_filename, epub_filename)
        print(f"EPUB generated successfully: {epub_filename}")

        # Get the absolute path of the HTML file
        abs_html_path = os.path.abspath(html_filename)
        print(f"HTML file created at: {abs_html_path}")
