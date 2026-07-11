import os
import json
import subprocess
import sys
from pathlib import Path

def main():
    print("====================================================")
    print("           Academic PDF Report Generator            ")
    print("====================================================")

    # 1. Load configuration details
    config_path = Path("report_config.json")
    if not config_path.exists():
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error parsing '{config_path}': {e}")
        sys.exit(1)

    print("Loaded configuration parameters:")
    for k, v in config.items():
        print(f"  - {k}: {v}")

    # 2. Load template file
    template_path = Path("project_report_template.html")
    if not template_path.exists():
        print(f"Error: Template file '{template_path}' not found.")
        sys.exit(1)

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
    except Exception as e:
        print(f"Error reading '{template_path}': {e}")
        sys.exit(1)

    # 3. Substitute values
    compiled_content = template_content
    for key, val in config.items():
        placeholder = f"{{{{{key}}}}}"
        compiled_content = compiled_content.replace(placeholder, str(val))

    # Save compiled HTML file
    compiled_html_path = Path("project_report.html")
    try:
        with open(compiled_html_path, "w", encoding="utf-8") as f:
            f.write(compiled_content)
        print(f"\nSuccessfully compiled intermediate HTML to '{compiled_html_path.resolve()}'")
    except Exception as e:
        print(f"Error writing compiled HTML: {e}")
        sys.exit(1)

    # 4. Locate Microsoft Edge or Google Chrome executable for PDF compilation
    # Common Windows executable paths for Chromium browsers
    paths_to_check = [
        # Edge paths
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # Chrome paths
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # Direct execution names if present in PATH
        "msedge.exe",
        "msedge",
        "chrome.exe",
        "chrome"
    ]

    browser_path = None
    for path in paths_to_check:
        if os.path.exists(path):
            browser_path = path
            break
        # If it's a bare command name, test if it is executable in shell
        if not path.startswith("C:"):
            try:
                subprocess.run([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                browser_path = path
                break
            except Exception:
                continue

    if not browser_path:
        print("\n[WARNING] Could not locate Microsoft Edge or Google Chrome in standard installation paths.")
        print("Please enter the absolute path to your browser executable (msedge.exe or chrome.exe),")
        print("or press Enter to exit and print the HTML file manually in your browser.")
        user_input = input("Browser path: ").strip().strip('"')
        if not user_input:
            print("\nIntermediate HTML generated successfully. You can open 'project_report.html' in your browser and print to PDF manually.")
            sys.exit(0)
        else:
            browser_path = user_input

    # 5. Convert compiled HTML to PDF
    pdf_output_name = "Stock_Market_Prediction_Report.pdf"
    pdf_output_path = Path(pdf_output_name).resolve()
    
    # We use file:// URI to resolve local assets correctly (e.g. screenshots)
    input_file_uri = compiled_html_path.resolve().as_uri()

    print(f"\nCompiling PDF using browser: '{browser_path}'...")
    print(f"Input URI: {input_file_uri}")
    print(f"Output Path: {pdf_output_path}")

    # Build PDF compile command
    cmd = [
        browser_path,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_output_path}",
        input_file_uri
    ]

    try:
        # Run subprocess to build report
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=30)
        
        # Verify the file was created and is not empty
        if pdf_output_path.exists() and pdf_output_path.stat().st_size > 0:
            print("\n====================================================")
            print("Success! PDF Report successfully generated!         ")
            print(f"File Name: {pdf_output_name}                         ")
            print(f"Location:  {pdf_output_path}                        ")
            print("====================================================")
            print("Note: If you add screenshots in the 'report_images/' folder,")
            print("simply re-run 'python generate_report.py' to compile them into the PDF.")
        else:
            print(f"\nError: Browser finished execution but '{pdf_output_name}' was not created or is empty.")
    except subprocess.TimeoutExpired:
        print("\nError: PDF conversion timed out after 30 seconds.")
    except subprocess.CalledProcessError as e:
        print(f"\nError executing PDF conversion command: {e}")
        print(f"Stdout: {e.stdout.decode(errors='replace')}")
        print(f"Stderr: {e.stderr.decode(errors='replace')}")
    except Exception as e:
        print(f"\nUnexpected error during PDF generation: {e}")

if __name__ == "__main__":
    main()
