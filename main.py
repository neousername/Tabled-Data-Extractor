import json
import os
import glob
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import creds
import ai_prompt

# Configure API
genai.configure(api_key=creds.api_key)

generation_config = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

# Using gemini-2.0-flash-exp for high quality extraction
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    generation_config=generation_config,
)


def process_single_image(args):
    """
    Helper function to process a single image.
    Args:
        args: A tuple containing (img_path, current_index, total_files)
    Returns:
        list: A list of extracted rows (dicts) or empty list if failed.
    """
    img_path, current_index, total_files = args
    # Reduced verbosity: Removed start/upload/analysis prints to avoid console overload

    uploaded_file = None
    new_rows = []

    try:
        uploaded_file = genai.upload_file(img_path)
        response = model.generate_content([ai_prompt.prompt, uploaded_file])

        raw_text = response.text.strip()

        # Simple sanitization
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        parsed_data = json.loads(raw_text)

        if isinstance(parsed_data, list):
            new_rows = parsed_data
        elif isinstance(parsed_data, dict):
            if "data" in parsed_data and isinstance(parsed_data["data"], list):
                new_rows = parsed_data["data"]
            else:
                new_rows = [parsed_data]
        else:
            print(f"[{current_index}/{total_files}] Error: Unexpected JSON format in {os.path.basename(img_path)}.")

        # Normalize keys
        for row in new_rows:
            if "CREATE DEAL FROM INT.." in row:
                row["CREATE DEAL FROM INT..."] = row.pop("CREATE DEAL FROM INT..")

    except json.JSONDecodeError:
        print(f"[{current_index}/{total_files}] Error: AI output was not valid JSON for {os.path.basename(img_path)}.")
    except Exception as e:
        print(f"[{current_index}/{total_files}] Error processing {os.path.basename(img_path)}: {e}")
    finally:
        if uploaded_file:
            try:
                uploaded_file.delete()
            except:
                pass
    
    return new_rows


def process_screenshots(screenshots_dir="Screenshots", output_json="data.json"):
    # Ensure the output JSON file exists
    if not os.path.exists(output_json):
        try:
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
        except Exception as e:
            print(f"Error creating {output_json}: {e}")

    files_to_process = sorted(glob.glob(os.path.join(screenshots_dir, "*.png")))
    total_files = len(files_to_process)

    if total_files == 0:
        print(f"No PNG files found in {screenshots_dir}")
        return

    print(f"Processing {total_files} pages. Note: 100 pages take approximately 10 seconds.")

    # Initialize or load existing data
    all_extracted_rows = []
    if os.path.exists(output_json):
        try:
            with open(output_json, "r", encoding="utf-8") as f:
                all_extracted_rows = json.load(f)
                if not isinstance(all_extracted_rows, list):
                    all_extracted_rows = []
        except:
            all_extracted_rows = []

    # Auto-cleanup and Resume logic
    RECORDS_PER_PAGE = 19

    # Check for partial pages
    remainder = len(all_extracted_rows) % RECORDS_PER_PAGE
    if remainder > 0:
        all_extracted_rows = all_extracted_rows[:-remainder]
        # Save immediately
        try:
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(all_extracted_rows, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cleaned data: {e}")

    existing_count = len(all_extracted_rows)
    files_to_skip = existing_count // RECORDS_PER_PAGE

    if files_to_skip > 0:
        # Slice the list of files
        if files_to_skip < len(files_to_process):
            files_to_process = files_to_process[files_to_skip:]
        else:
            files_to_process = []

    # Prepare arguments for the worker function
    # We create a list of tuples: (img_path, visual_index, total_files)
    worker_args = []
    for i, img_path in enumerate(files_to_process):
        current_index = i + 1 + files_to_skip
        worker_args.append((img_path, current_index, total_files))

    # Use ThreadPoolExecutor to process files concurrently
    # Max workers set to 100 based on user request
    with ThreadPoolExecutor(max_workers=100) as executor:
        # map returns results in the order of the iterable, ensuring we save sequentially
        results = executor.map(process_single_image, worker_args)

        for new_rows in results:
            # Save immediately if we got data
            if new_rows:
                all_extracted_rows.extend(new_rows)
                try:
                    with open(output_json, "w", encoding="utf-8") as f:
                        json.dump(all_extracted_rows, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    print(f"Error saving to JSON: {e}")

    print(
        f"\nDONE! Final data count: {len(all_extracted_rows)} records in {output_json}"
    )


if __name__ == "__main__":
    process_screenshots()
