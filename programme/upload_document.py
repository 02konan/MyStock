# import requests

# def upload_document(file_path, document_type):
#     url = 'http://localhost:5000/upload_document'  # URL de votre endpoint Flask
#     files = {'file': open(file_path, 'rb')}
#     data = {'document_type': document_type}
    
#     try:
#         response = requests.post(url, files=files, data=data)
#         if response.status_code == 200:
#             print("Document uploaded successfully!")
#         else:
#             print(f"Failed to upload document. Status code: {response.status_code}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
