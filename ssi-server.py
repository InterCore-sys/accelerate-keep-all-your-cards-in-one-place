import http.server
import socketserver
import os
import re

# Define the port the server will run on
PORT = 8000

class SSIRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom request handler that processes simple SSI directives.
    """
    # Regex to find SSI include directives
    ssi_include_regex = re.compile(r'')

    def do_GET(self):
        """Serve a GET request, processing SSI if the file ends in .shtml."""
        # Get the path to the requested file
        filepath = self.translate_path(self.path)

        # Check if it's an SSI file
        if filepath.endswith(".shtml"):
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.process_ssi(filepath)
            else:
                self.send_error(404, "File Not Found")
        else:
            # For non-SSI files, use the default handler
            super().do_GET()

    def process_ssi(self, filepath):
        """Reads an SHTML file, processes includes, and sends the response."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Process all include directives found in the content
            processed_content = self.ssi_include_regex.sub(self.include_handler(filepath), content)
            
            # Encode the final content to bytes
            encoded_content = processed_content.encode('utf-8')

            # Send the response headers
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(encoded_content)))
            self.end_headers()

            # Send the actual content
            self.wfile.write(encoded_content)

        except Exception as e:
            self.send_error(500, f"Error processing SSI file: {e}")

    def include_handler(self, base_filepath):
        """
        Returns a function that handles the substitution for a single include match.
        This is used as the replacer function for re.sub().
        """
        base_dir = os.path.dirname(base_filepath)

        def handle_match(match):
            # Get the path of the file to include, relative to the current file
            include_path = os.path.join(base_dir, match.group(1))
            
            if os.path.exists(include_path):
                with open(include_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"[Could not include '{match.group(1)}': File not found]"
        
        return handle_match

# --- Server Setup ---
Handler = SSIRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🐍 Serving on http://localhost:{PORT}")
    print("Serving files from directory:", os.getcwd())
    print("SSI processing enabled for .shtml files.")
    httpd.serve_forever()