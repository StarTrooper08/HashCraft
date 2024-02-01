from flask import Flask, render_template, request, send_file
import os
import requests
from pyhtml2pdf import converter
import re
import subprocess

app = Flask(__name__)

def fetch_html_content(host, slug):
    url = "https://gql.hashnode.com/"

    query = f"""
    query Publication {{
      publication(host: "{host}") {{
        post(slug: "{slug}") {{
          title
          content {{
            html
          }}
          author {{
            name
          }}
        }}
      }}
    }}
    """

    data = {"query": query}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()
        title = result.get("data", {}).get("publication", {}).get("post", {}).get("title", "")
        author_name = result.get("data", {}).get("publication", {}).get("post", {}).get("author", {}).get("name", "")
        html_content = result.get("data", {}).get("publication", {}).get("post", {}).get("content", {}).get("html", "")
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

def extract_host_and_slug(blog_link):
    # Assuming the format is "https://host/slug"
    parts = blog_link.split("/")
    host = parts[2] if len(parts) > 2 else ""
    slug = parts[3] if len(parts) > 3 else ""
    return host, slug

@app.route('/', methods=['GET', 'POST'])
def index():
    host = ""
    slug = ""
    title = ""
    author_name = ""
    html_content = ""

    if request.method == 'POST':
        blog_link = request.form['blog_link']
        host, slug = extract_host_and_slug(blog_link)
        title, author_name, html_content = fetch_html_content(host, slug)

    return render_template('index.html', host=host, slug=slug, title=title, author_name=author_name, html_content=html_content)

@app.route('/convert_pdf', methods=['POST'])
def convert_pdf():
    host = request.form['host']
    slug = request.form['slug']
    title, author_name, html_content = fetch_html_content(host, slug)

    cleaned_html = remove_emojis(html_content)
    html_filename = create_html_file(cleaned_html)

    pdf_filename = "article.pdf"
    convert_html_to_pdf(title, author_name, html_filename, pdf_filename)

    # Move removal outside the if condition
    # Remove HTML file after both PDF and EPUB conversions
    if os.path.exists(html_filename):
        os.remove(html_filename)

    # Provide a download link for the generated PDF
    return send_file(pdf_filename, as_attachment=True)

@app.route('/convert_epub', methods=['POST'])
def convert_epub():
    host = request.form['host']
    slug = request.form['slug']
    title, _, html_content = fetch_html_content(host, slug)

    cleaned_html = remove_emojis(html_content)
    html_filename = create_html_file(cleaned_html)

    epub_filename = "article.epub"
    convert_html_to_epub(title, html_filename, epub_filename)

    # Move removal outside the if condition
    # Remove HTML file after both PDF and EPUB conversions
    if os.path.exists(html_filename):
        os.remove(html_filename)

    # Provide a download link for the generated EPUB
    return send_file(epub_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
