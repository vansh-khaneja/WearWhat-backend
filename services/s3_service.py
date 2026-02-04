from minio import Minio
from minio.error import S3Error
from config import MINIO_ENDPOINT, MINIO_PUBLIC_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, MINIO_SECURE
import uuid
import json
from io import BytesIO

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# Ensure bucket exists and is public
if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
    minio_client.make_bucket(MINIO_BUCKET_NAME)
    print(f"Created bucket: {MINIO_BUCKET_NAME}")

# Set bucket policy to public read
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
            "Resource": f"arn:aws:s3:::{MINIO_BUCKET_NAME}"
        },
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{MINIO_BUCKET_NAME}/*"
        }
    ]
}
minio_client.set_bucket_policy(MINIO_BUCKET_NAME, json.dumps(policy))
print(f"Set public read policy on bucket: {MINIO_BUCKET_NAME}")


def upload_image(file, folder: str = "wearwhat/wardrobe") -> str:
    """Upload image to MinIO and return public URL."""
    # Generate unique filename
    file_extension = "png"
    filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

    # Handle both file objects and BytesIO
    if hasattr(file, 'read'):
        file.seek(0)
        file_content = file.read()
        file.seek(0)
    else:
        file_content = file

    # Convert to BytesIO if needed
    if isinstance(file_content, bytes):
        file_data = BytesIO(file_content)
        file_size = len(file_content)
    else:
        file_data = file
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Seek back to start

    # Upload to MinIO
    minio_client.put_object(
        bucket_name=MINIO_BUCKET_NAME,
        object_name=filename,
        data=file_data,
        length=file_size,
        content_type='image/png'
    )

    # Return public URL (use MINIO_PUBLIC_URL for browser access)
    protocol = "https" if MINIO_SECURE else "http"
    url = f"{protocol}://{MINIO_PUBLIC_URL}/{MINIO_BUCKET_NAME}/{filename}"
    return url


def upload_profile_image(file) -> str:
    """Upload profile image to S3."""
    return upload_image(file, folder="wearwhat/profiles")


def upload_outfit_image(file) -> str:
    """Upload combined outfit image to S3."""
    return upload_image(file, folder="outfit_recommendations")


def upload_studio_image(file) -> str:
    """Upload studio generated image to S3."""
    return upload_image(file, folder="wearwhat/studio")


def delete_image(image_url: str) -> bool:
    """Delete image from MinIO by URL."""
    if not image_url:
        return False

    try:
        # Check if it's a Cloudinary URL (legacy) - skip deletion
        if "cloudinary.com" in image_url:
            print(f"Skipping Cloudinary URL (legacy): {image_url}")
            return True  # Return True as we don't want to fail the operation

        # Extract object name from URL
        # URL format: http://localhost:9000/bucket/folder/filename.png
        protocol = "https" if MINIO_SECURE else "http"
        prefix = f"{protocol}://{MINIO_PUBLIC_URL}/{MINIO_BUCKET_NAME}/"

        print(f"[DEBUG] Trying to delete: {image_url}")
        print(f"[DEBUG] Expected prefix: {prefix}")

        if image_url.startswith(prefix):
            object_name = image_url[len(prefix):]
            minio_client.remove_object(MINIO_BUCKET_NAME, object_name)
            print(f"Deleted from MinIO: {object_name}")
            return True
        else:
            # Try alternative: extract path after bucket name
            bucket_marker = f"/{MINIO_BUCKET_NAME}/"
            if bucket_marker in image_url:
                object_name = image_url.split(bucket_marker, 1)[1]
                minio_client.remove_object(MINIO_BUCKET_NAME, object_name)
                print(f"Deleted from MinIO (alt): {object_name}")
                return True

            print(f"URL doesn't match MinIO format: {image_url}")
            return False
    except Exception as e:
        print(f"Failed to delete from MinIO: {e}")
        return False
