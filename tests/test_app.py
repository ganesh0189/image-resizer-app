import unittest
import os
import io
from PIL import Image
from app import create_app
from app.config import Config

class TestImageResizerApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.app.config['TESTING'] = True
        self.app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
        self.app.config['MAX_FILE_SIZE'] = 10 * 1024 * 1024  # 10MB per file limit
        self.client = self.app.test_client()
        self.test_image = self.create_test_image()

    def tearDown(self):
        # Clean up any test files
        if os.path.exists('tests/large_file.bin'):
            os.remove('tests/large_file.bin')

    def create_test_image(self):
        # Create a test image in memory
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return img_io

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Image Resizer', response.data)

    def test_resize_image_success(self):
        data = {
            'file': (self.test_image, 'test.jpg'),
            'width': '50',
            'height': '50'
        }
        response = self.client.post('/resize', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        json_data = response.get_json()
        self.assertIn('download_url', json_data)
        self.assertIn('original_size', json_data)
        self.assertIn('new_size', json_data)

    def test_resize_image_invalid_dimensions(self):
        data = {
            'file': (self.test_image, 'test.jpg'),
            'width': '-50',
            'height': '50'
        }
        response = self.client.post('/resize', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'Width and height must be positive numbers')

    def test_compress_image_success(self):
        data = {
            'file': (self.test_image, 'test.jpg'),
            'target_size_kb': '50',
            'quality': '80'
        }
        response = self.client.post('/compress', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        json_data = response.get_json()
        self.assertIn('download_url', json_data)
        self.assertIn('original_size', json_data)
        self.assertIn('new_size', json_data)

    def test_compress_image_invalid_size(self):
        data = {
            'file': (self.test_image, 'test.jpg'),
            'target_size_kb': '-50',
            'quality': '80'
        }
        response = self.client.post('/compress', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'Target size must be positive')

    def test_missing_file(self):
        data = {
            'width': '50',
            'height': '50'
        }
        response = self.client.post('/resize', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'No file provided')

    def test_invalid_file_type(self):
        data = {
            'file': (io.BytesIO(b'not an image'), 'test.txt'),
            'width': '50',
            'height': '50'
        }
        response = self.client.post('/resize', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'Invalid file type')

    def test_file_too_large(self):
        # Create a file that is 16MB + 1 byte
        file_size = (16 * 1024 * 1024) + 1
        data = b'0' * file_size
        
        with open('tests/large_file.bin', 'wb') as f:
            f.write(data)
        
        with open('tests/large_file.bin', 'rb') as f:
            data = {
                'file': (f, 'large_file.bin'),
                'width': '50',
                'height': '50'
            }
            response = self.client.post('/resize', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 413)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'File size exceeds limit')

    def test_unexpected_error(self):
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 500)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.')

if __name__ == '__main__':
    unittest.main() 