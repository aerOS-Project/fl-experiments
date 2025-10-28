import requests

def upload_compatible_model():
    print("Uploading formatted ZIP model to FL Repository...")
    
    url = 'http://localhost:9013/model/migration_predictor/v1'
    
    try:
        with open('./setup/model/migration_predictor_v1.zip', 'rb') as model_file:
            files = {
                'file': ('migration_predictor_v1.zip', model_file, 'application/octet-stream')
            }
            response = requests.put(url, files=files)
            
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 204:
                print("Model uploaded successfully!")
            else:
                print("Model upload failed!")
                
    except FileNotFoundError:
        print("Model file not found!")
    except Exception as e:
        print(f"Error uploading model: {e}")

if __name__ == "__main__":
    upload_compatible_model()