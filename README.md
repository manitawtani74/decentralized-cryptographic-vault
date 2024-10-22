Secure File Storage Solution - API Documentation
This solution enables secure, decentralized file storage, leveraging encryption, chunking, random bucket storage, and a hash-based retrieval mechanism. This API-based system is built using Django and runs in a containerized environment on Google Cloud Kubernetes.

Overview
File Upload
The file upload API allows end-users to securely upload files by:

Encrypting the file using the AES algorithm and a user-provided password.
Splitting the encrypted file into configurable-size chunks.
Randomly storing each chunk in GCP Cloud Storage.
Saving the storage map in a PostgreSQL database.
Returning a unique hash as a reference for future file retrieval.
File Retrieval
The file retrieval API requires the unique hash to:

Fetch the file-chunk-storage map from the database.
Download the individual chunks from GCP Cloud Storage.
Reassemble the file, decrypt it with the user-provided password.
Return a secure download link for the file.
Technology Stack
Django: The web framework used for building the API.
PostgreSQL: Used to store the mapping of file chunks and their storage locations.
GCP Cloud Storage: Where the file chunks are securely stored in random buckets.
AES Encryption: Ensures the files are securely encrypted before being uploaded.
Google Cloud Kubernetes: The entire system is deployed in containers on GCP Kubernetes.
API Endpoints
1. File Upload API
Endpoint: /api/upload

Method: POST

Request Parameters:

file: The file to be uploaded.
password: The password for AES encryption.
chunk_size (optional): Size of the file chunks, in bytes. Default: 1 MB.
Process:

The file is encrypted using AES encryption with the provided password.
It is split into chunks of the specified size.
Each chunk is stored in a random GCP Cloud Storage bucket.
A storage map (which bucket and location each chunk resides in) is saved in PostgreSQL.
A unique hash is generated and returned to the user.
Response:

json
Copy code
{
  "status": "success",
  "hash": "unique_hash_value"
}
2. File Retrieval API
Endpoint: /api/retrieve/<hash>

Method: GET

Request Parameters:

password: The password used for file encryption.
Process:

The API fetches the storage map corresponding to the provided hash from PostgreSQL.
It retrieves the file chunks from GCP Cloud Storage.
The chunks are reassembled into the original encrypted file.
The file is decrypted using the provided password.
A secure download link is returned.
Response:

json
Copy code
{
  "status": "success",
  "download_link": "https://download-link"
}
Use Cases
1. Secure Document Storage
Organizations that need to securely store sensitive documents (e.g., legal, financial) can leverage this solution. The files are encrypted and broken into chunks, ensuring decentralized storage and preventing unauthorized access to complete files.

2. Decentralized Backup System
By distributing file chunks across multiple random GCP Cloud Storage buckets, this solution offers a decentralized and resilient backup mechanism. Even if a bucket is compromised, unauthorized access to the full file is prevented.

3. Regulatory Compliance
Industries like healthcare and finance can use this system to meet regulatory standards by ensuring that customer data is stored securely, encrypted, and distributed to prevent centralized vulnerabilities.

System Architecture
Django Backend:

Handles API requests for file uploads and retrievals.
Manages the encryption, chunking, and storage logic.
PostgreSQL Database:

Stores a map linking the file chunks to their respective storage locations in GCP Cloud Storage.
GCP Cloud Storage:

Stores the encrypted file chunks in randomly assigned buckets.
Google Cloud Kubernetes:

Ensures that the application runs reliably and scales as needed by hosting the Django application and PostgreSQL in containers.
Detailed File Upload Process
File Encryption:
The uploaded file is encrypted using AES encryption with a password provided by the user.
Chunking:
The encrypted file is split into smaller chunks based on a configurable chunk size (default: 1MB).
Random Storage:
Each chunk is randomly assigned and stored in a different GCP Cloud Storage bucket to ensure decentralization and enhance security.
Storage Mapping:
The mapping between file chunks and their respective storage locations (bucket name and path) is stored in the PostgreSQL database.
Hash Generation:
A unique hash is generated, which links to the file's storage map in the database. This hash is provided to the user for future retrieval.
Detailed File Retrieval Process
Storage Map Retrieval:
When a user provides the unique hash, the system retrieves the corresponding file-chunk-storage map from PostgreSQL.
Chunk Download:
The file chunks are fetched from the respective GCP Cloud Storage buckets.
File Reassembly:
The chunks are reassembled into the encrypted file.
Decryption:
The reassembled file is decrypted using the user-provided password.
Download Link:
A secure link is generated, allowing the user to download the decrypted file.
Deployment
The entire application runs within a Google Cloud Kubernetes cluster for scalability and reliability. The PostgreSQL database is hosted on Google Cloud, and GCP Cloud Storage is used for storing the encrypted file chunks.

Key components in deployment:

Google Kubernetes Engine (GKE): Hosts the Django app and PostgreSQL containers.
Google Cloud Storage (GCS): Secure storage for the encrypted file chunks.
Google Cloud IAM: Ensures only authorized users/services can access the GCS buckets.
Security Considerations
AES Encryption: The file is encrypted with AES, a strong encryption standard, using a user-provided password.
Decentralized Storage: Each file chunk is randomly distributed across different GCP storage buckets, ensuring decentralization and minimizing risk.
Password-Protected Retrieval: Only the correct password can decrypt the retrieved file, adding an extra layer of security.
Secure Buckets: Each storage bucket is secured using Google Cloud's IAM policies to prevent unauthorized access.