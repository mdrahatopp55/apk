#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import os
import sys
import json
from pathlib import Path

class WorkingHTMLEncoder:
    def __init__(self):
        print("\033[96m" + "="*60)
        print("      ERROR X SAJU - HTML ENCODER (WORKING)")
        print("="*60 + "\033[0m")
    
    def encode_html(self, html_content):
        """HTML encode     """
        try:
            # Method 1: Simple Base64 encoding (browser compatible)
            encoded = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            
            # Method 2: Add JavaScript decoder wrapper
            wrapper = f"""<!DOCTYPE html>
<html>
<head>
    <title>Encoded Page</title>
    <script>
    function decodePage() {{
        try {{
            // Base64 decode
            const encoded = "{encoded}";
            const decoded = atob(encoded);
            
            // Write to document
            document.open();
            document.write(decoded);
            document.close();
            
            // Add style for loading indicator
            const style = document.createElement('style');
            style.textContent = `
                .decode-success {{
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    background: #00ff00;
                    color: black;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 12px;
                }}
            `;
            document.head.appendChild(style);
            
            // Show success message
            const msg = document.createElement('div');
            msg.className = 'decode-success';
            msg.textContent = ' Decoded Successfully';
            document.body.appendChild(msg);
            
            setTimeout(() => msg.remove(), 3000);
            
        }} catch(error) {{
            document.body.innerHTML = '<h1 style="color:red">Decode Error: ' + error + '</h1>';
        }}
    }}
    
    // Auto decode on page load
    window.onload = decodePage;
    </script>
</head>
<body>
    <div style="text-align:center; padding:50px;">
        <h2> ENCODED HTML PAGE</h2>
        <p>Decoding in progress...</p>
        <div style="margin:30px;">
            <div class="spinner"></div>
        </div>
        <p><small>ERROR X SAJU Encoder v1.0</small></p>
    </div>
    
    <style>
        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }}
    </style>
</body>
</html>"""
            
            return wrapper
            
        except Exception as e:
            return f"<html><body><h1>Encoding Error: {str(e)}</h1></body></html>"
    
    def decode_html(self, encoded_content):
        """Encoded HTML decode """
        try:
            # Find the encoded string in the wrapper
            if 'const encoded = "' in encoded_content:
                start = encoded_content.find('const encoded = "') + len('const encoded = "')
                end = encoded_content.find('"', start)
                encoded_str = encoded_content[start:end]
                
                # Decode from Base64
                decoded = base64.b64decode(encoded_str).decode('utf-8')
                return decoded
            else:
                # Try direct Base64 decode
                decoded = base64.b64decode(encoded_content).decode('utf-8')
                return decoded
                
        except Exception as e:
            return f"<html><body><h1>Decoding Error: {str(e)}</h1></body></html>"
    
    def process_file(self, input_file, output_file=None, action='encode'):
        """ process """
        try:
            # Check if file exists
            if not os.path.exists(input_file):
                print(f"\033[91m File not found: {input_file}\033[0m")
                return False
            
            # Read file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\033[92m File loaded: {input_file}\033[0m")
            print(f"\033[93mSize: {len(content)} bytes\033[0m")
            
            # Process
            if action == 'encode':
                result = self.encode_html(content)
                
                # Auto generate output filename
                if not output_file:
                    base_name = os.path.splitext(input_file)[0]
                    output_file = f"{base_name}_encoded.html"
                
                action_text = "Encoded"
                color = "\033[96m"
                
            else:  # decode
                result = self.decode_html(content)
                
                if not output_file:
                    base_name = os.path.splitext(input_file)[0]
                    if '_encoded' in base_name:
                        base_name = base_name.replace('_encoded', '_decoded')
                    else:
                        base_name = f"{base_name}_decoded"
                    output_file = f"{base_name}.html"
                
                action_text = "Decoded"
                color = "\033[95m"
            
            # Save output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            
            print(f"{color} {action_text} successfully!\033[0m")
            print(f"\033[92mOutput saved: {output_file}\033[0m")
            print(f"\033[93mOutput size: {len(result)} bytes\033[0m")
            
            # Show preview
            print("\n\033[94m" + "="*60)
            print(" PREVIEW (first 200 chars):")
            print("="*60 + "\033[0m")
            print(result[:200] + "..." if len(result) > 200 else result)
            
            # Instructions
            print("\n\033[92m" + " INSTRUCTIONS:")
            print("-" * 50 + "\033[0m")
            print(f"1. Open in browser: \033[93m{output_file}\033[0m")
            print("2. File will auto-decode in browser")
            print("3. Works in Chrome, Firefox, Edge")
            
            return True
            
        except Exception as e:
            print(f"\033[91m Error: {str(e)}\033[0m")
            return False
    
    def show_menu(self):
        """ """
        while True:
            print("\n" + "\033[96m" + "="*60)
            print("             HTML ENCODER/DECODER MENU")
            print("="*60 + "\033[0m")
            
            print("\033[93m1.  Encode HTML File")
            print("2.  Decode HTML File")
            print("3.  Encode Text Input")
            print("4.  Decode Text Input")
            print("5.   Quick Test")
            print("0.  Exit\033[0m")
            
            choice = input("\n\033[94mSelect option: \033[0m")
            
            if choice == '1':
                self.encode_file_menu()
            elif choice == '2':
                self.decode_file_menu()
            elif choice == '3':
                self.encode_text_menu()
            elif choice == '4':
                self.decode_text_menu()
            elif choice == '5':
                self.quick_test()
            elif choice == '0':
                print("\n\033[92m Thanks for using ERROR X SAJU Encoder!\033[0m")
                break
            else:
                print("\033[91mInvalid option!\033[0m")
    
    def encode_file_menu(self):
        """Encode  """
        print("\n\033[94m" + "="*50)
        print("         ENCODE HTML FILE")
        print("="*50 + "\033[0m")
        
        input_file = input("\033[93mEnter HTML file path: \033[0m")
        
        if not input_file:
            print("\033[91mNo file specified!\033[0m")
            return
        
        output_file = input("\033[93mOutput file (press Enter for auto-name): \033[0m")
        
        self.process_file(input_file, output_file, 'encode')
        
        input("\n\033[90mPress Enter to continue...\033[0m")
    
    def decode_file_menu(self):
        """Decode  """
        print("\n\033[94m" + "="*50)
        print("         DECODE HTML FILE")
        print("="*50 + "\033[0m")
        
        input_file = input("\033[93mEnter encoded file path: \033[0m")
        
        if not input_file:
            print("\033[91mNo file specified!\033[0m")
            return
        
        output_file = input("\033[93mOutput file (press Enter for auto-name): \033[0m")
        
        self.process_file(input_file, output_file, 'decode')
        
        input("\n\033[90mPress Enter to continue...\033[0m")
    
    def encode_text_menu(self):
        """Encode text input"""
        print("\n\033[94m" + "="*50)
        print("         ENCODE TEXT INPUT")
        print("="*50 + "\033[0m")
        
        print("\033[93mPaste your HTML code (Ctrl+D when done):\033[0m")
        print("\033[90m" + "-"*50 + "\033[0m")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        html_content = '\n'.join(lines)
        
        if not html_content.strip():
            print("\033[91mNo input provided!\033[0m")
            return
        
        result = self.encode_html(html_content)
        
        print("\n\033[92m" + "="*50)
        print(" ENCODED OUTPUT:")
        print("="*50 + "\033[0m")
        print(result)
        
        save = input("\n\033[93mSave to file? (y/n): \033[0m").lower()
        if save == 'y':
            filename = input("\033[93mFilename: \033[0m")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\033[92m Saved to {filename}\033[0m")
        
        input("\n\033[90mPress Enter to continue...\033[0m")
    
    def decode_text_menu(self):
        """Decode text input"""
        print("\n\033[94m" + "="*50)
        print("         DECODE TEXT INPUT")
        print("="*50 + "\033[0m")
        
        print("\033[93mPaste encoded content (Ctrl+D when done):\033[0m")
        print("\033[90m" + "-"*50 + "\033[0m")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        encoded_content = '\n'.join(lines)
        
        if not encoded_content.strip():
            print("\033[91mNo input provided!\033[0m")
            return
        
        result = self.decode_html(encoded_content)
        
        print("\n\033[92m" + "="*50)
        print(" DECODED OUTPUT:")
        print("="*50 + "\033[0m")
        print(result)
        
        save = input("\n\033[93mSave to file? (y/n): \033[0m").lower()
        if save == 'y':
            filename = input("\033[93mFilename: \033[0m")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\033[92m Saved to {filename}\033[0m")
        
        input("\n\033[90mPress Enter to continue...\033[0m")
    
    def quick_test(self):
        """Quick test  """
        print("\n\033[94m" + "="*50)
        print("         QUICK TEST")
        print("="*50 + "\033[0m")
        
        # Create a test HTML file
        test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>
        body {
            font-family: Arial;
            background: linear-gradient(45deg, #ff0066, #00ccff);
            color: white;
            text-align: center;
            padding: 50px;
        }
        h1 {
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .success {
            background: rgba(0,255,0,0.2);
            padding: 20px;
            border-radius: 10px;
            margin: 20px;
            border: 2px solid #00ff00;
        }
    </style>
</head>
<body>
    <h1> ERROR X SAJU ENCODER </h1>
    <div class="success">
        <h2>Encoding Successful!</h2>
        <p>This page was encoded and decoded properly.</p>
        <p>JavaScript is working: <span id="demo"></span></p>
        <button onclick="showAlert()">Click Me</button>
    </div>
    
    <script>
        document.getElementById('demo').textContent = ' Test Passed!';
        function showAlert() {
            alert(' Encoder is working perfectly!');
        }
    </script>
</body>
</html>"""
        
        # Save test file
        with open('test_page.html', 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        print("\033[92m Test HTML created: test_page.html\033[0m")
        
        # Encode it
        print("\033[93mEncoding test file...\033[0m")
        encoded = self.encode_html(test_html)
        
        with open('test_encoded.html', 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        print("\033[92m Encoded file created: test_encoded.html\033[0m")
        
        # Show instructions
        print("\n\033[96m" + " TEST INSTRUCTIONS:")
        print("-" * 50 + "\033[0m")
        print("1. Open test_encoded.html in browser")
        print("2. It should auto-decode and show the test page")
        print("3. Click the button to test JavaScript")
        print("4. If everything works, encoder is OK")
        
        input("\n\033[90mPress Enter to continue...\033[0m")

def main():
    """Main function"""
    try:
        encoder = WorkingHTMLEncoder()
        encoder.show_menu()
    except KeyboardInterrupt:
        print("\n\n\033[93m Program interrupted\033[0m")
    except Exception as e:
        print(f"\033[91mError: {str(e)}\033[0m")

if __name__ == "__main__":
    main()