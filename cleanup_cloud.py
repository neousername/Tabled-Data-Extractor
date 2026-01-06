import google.generativeai as genai
import creds

# Configure the API key
genai.configure(api_key=creds.api_key)

def delete_all_cloud_files():
    print("Listing files in Gemini Cloud for deletion...")
    try:
        files = list(genai.list_files())
        
        if not files:
            print("No files found to delete.")
            return

        print(f"Found {len(files)} files. Starting deletion...")
        
        for f in files:
            print(f"Deleting {f.name} ({f.display_name})...")
            f.delete()
            print("  -> Deleted.")
            
        print("\nAll files have been cleared from the cloud.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    delete_all_cloud_files()
