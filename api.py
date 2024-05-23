from flask import Flask, request, jsonify
from rembg import remove
import io
from PIL import Image
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name='dpsvsblcz',  # Replace with your Cloudinary cloud name
    api_key='796211564876846',  # Replace with your Cloudinary API key
    api_secret='SseLecsEbOtLTVDuMuFY_JiiL-o'  # Replace with your Cloudinary API secret
)

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'image' not in request.files:
        return jsonify({'success': 'false', 'message': 'No image file provided'}), 400

    if 'tag' not in request.form:
        return jsonify({'success': 'false', 'message': 'No tag provided'}), 400

    file = request.files['image']
    user_tag = request.form['tag']

    if file.filename == '':
        return jsonify({'success': 'false', 'message': 'No selected file'}), 400

    try:
        # Read image file
        input_image = Image.open(file)
        # Convert to bytes
        input_bytes = io.BytesIO()
        input_image.save(input_bytes, format=input_image.format)
        input_bytes = input_bytes.getvalue()

        # Remove background
        output_bytes = remove(input_bytes)

        # Convert bytes to image
        output_image = Image.open(io.BytesIO(output_bytes))

        # Save output image to a BytesIO object
        output_io = io.BytesIO()
        output_image.save(output_io, format='PNG')
        output_io.seek(0)

        # Delete old images with the same tag
        resources = cloudinary.api.resources_by_tag(user_tag)
        for resource in resources.get('resources', []):
            cloudinary.uploader.destroy(resource['public_id'])

        # Upload new image to Cloudinary with the provided tag
        response = cloudinary.uploader.upload(output_io, resource_type='image', tags=[user_tag])

        # Get the URL of the uploaded image
        image_url = response.get('secure_url')

        return jsonify({
            'success': 'true',
            'message': 'Background removed successfully.',
            'image_url': image_url
        }), 200

    except Exception as e:
        return jsonify({'success': 'false', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run()
