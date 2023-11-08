from flask import Flask, jsonify, send_file, send_from_directory, url_for
import io, os
import numpy as np
from matplotlib import pyplot as plt
from sentinelhub import CRS, BBox, WmsRequest, DataCollection, SHConfig
from datetime import datetime


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello world!  Your web application is working!"

    @app.route('/download_image')
    def download_image():
        config = SHConfig()
        config.instance_id = "36a1bef1-0c7a-4801-ad5e-50d1dab78d55"

        # It's assumed that you have set the instance ID and other configurations in your SHConfig already.

        betsiboka_coords_wgs84 = (46.16, -16.15, 46.51, -15.58)
        betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
        wms_true_color_request = WmsRequest(
            data_collection=DataCollection.SENTINEL2_L1C,
            layer='TRUE-COLOR-S2L2A',
            bbox=betsiboka_bbox,
            time='latest',
            width=512,
            height=856,
            config=config
        )

        wms_true_color_img = wms_true_color_request.get_data()
        image = wms_true_color_img[-1]  # Take the last image from the list

        # Save the image to a BytesIO object
        image_bytes = io.BytesIO()
        plt.imsave(image_bytes, image, format='png')
        image_bytes.seek(0)  # Go to the beginning of the IO stream

        save_directory = 'images'  # Use a relative path in Replit

        # Make sure the directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        timestamp = datetime.now()

        # Convert the datetime to a timestamp (int)
        timestamp_int = int(timestamp.timestamp())

        filename = f"satellite_image_{timestamp_int}.png"

        # Full path for the image
        file_path = os.path.join(save_directory, filename)

        # Save the image to the specified directory
        plt.imsave(file_path, image, format='png')

        print(f"Image saved to {file_path}")

        return f"/show_image/{timestamp_int}"

    # xyz.com./show_image/id=timestamp

    @app.route('/show_image/<int:timestamp>')
    def show_image(timestamp):
        # Get the list of files in the images folder
        image_folder = 'images'  # Change this to the path of your images folder
        image_files = os.listdir(image_folder)

        # Iterate through the files and check if any match the specified timestamp
        for filename in image_files:
            # Check if the filename matches the format "satellite_image_timestamp.png"
            if filename.startswith('satellite_image_') and filename.endswith(f'{timestamp}.png'):
                # Generate the full URL to the matched image using url_for
                image_url = url_for('static', filename=f'{image_folder}/{filename}', _external=True)
                # Return the URL in a JSON response
                return jsonify({'download_url': image_url})

        # 1699317720
        # If no matching image is found, return an error response
        return jsonify({'error': 'Image not found for the specified timestamp'}), 404

    @app.route('/.well-known/ai-plugin.json')
    def serve_ai_plugin():
        return send_from_directory('.',
                                   'ai-plugin.json',
                                   mimetype='application/json')

    @app.route('/openapi.yaml')
    def serve_openapi_yaml():
        return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

    return app

# if __name__ == '__main__':
#   app.run(host='0.0.0.0', port=81)
