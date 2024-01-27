import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def fetch_data():
    url = "https://gql.hashnode.com/"
    
    # Define your GraphQL query
    query = """
    query Publication {
      publication(host: "atharva08.hashnode.dev") {
        isTeam
        title
        post(slug: "efficiency-unleashed-dockerizing-and-optimizing-a-fastapi-app-with-slimtoolkit-and-github-actions") {
          title
          content {
            markdown
          }
          author {
            name
          }
        }
      }
    }
    """

    # Prepare the request payload
    data = {"query": query}

    # Make the GraphQL request
    response = requests.post(url, json=data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()
        return result
    else:
        print(f"GraphQL request failed with status code {response.status_code}: {response.text}")
        return None

def split_text(text, max_length):
    """
    Split text into lines with a maximum length.
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        if sum(len(word) for word in current_line) + len(current_line) + len(word) <= max_length:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def generate_pdf(data):
    if data:
        pdf_filename = "output.pdf"
        
        # Create a PDF
        c = canvas.Canvas(pdf_filename, pagesize=letter)

        # Extract relevant data from the API response
        title = data["data"]["publication"]["post"]["title"]
        content = data["data"]["publication"]["post"]["content"]["markdown"]
        author_name = data["data"]["publication"]["post"]["author"]["name"]

        # Add title to the PDF
        c.setFont("Helvetica", 12)
        title_lines = split_text(title, 80)  # Adjust the max_length as needed
        for line_number, line in enumerate(title_lines):
            c.drawString(100, 750 - line_number * 12, line)

        # Add content to the PDF
        c.setFont("Helvetica", 10)
        content_lines = split_text(content, 80)  # Adjust the max_length as needed
        for line_number, line in enumerate(content_lines):
            c.drawString(100, 730 - line_number * 12, line)

        # Add author name to the footer
        c.setFont("Helvetica", 8)
        c.drawString(100, 50, f"Author: {author_name}")

        # Save the PDF
        c.save()
        print(f"PDF generated successfully: {pdf_filename}")

if __name__ == "__main__":
    api_response = fetch_data()
    generate_pdf(api_response)
