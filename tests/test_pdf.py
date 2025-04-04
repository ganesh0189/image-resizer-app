import unittest
import os
import io
import tempfile
from PIL import Image
from app import create_app
from app.config import Config
from werkzeug.datastructures import MultiDict, FileStorage

class SizedBytesIO(io.BytesIO):
    def __init__(self, data):
        super().__init__(data)
        self._size = len(data)

    def __len__(self):
        return self._size

class TestPDFConversion(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.test_images = [self.create_test_image() for _ in range(2)]
        self.uploads_dir = os.path.join(tempfile.gettempdir(), 'image_resizer_uploads')
        if not os.path.exists(self.uploads_dir):
            os.makedirs(self.uploads_dir)

    def tearDown(self):
        # Clean up test files
        for file in os.listdir(self.uploads_dir):
            if file.endswith('.pdf'):
                os.remove(os.path.join(self.uploads_dir, file))

    def create_test_image(self):
        # Create a test image in memory
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return img_io

    def test_convert_to_pdf_no_files(self):
        response = self.client.post('/convert-to-pdf', data={}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'No files provided')

    def test_convert_to_pdf_invalid_file_type(self):
        data = {
            'files': [(io.BytesIO(b'not an image'), 'test.txt')],
            'order': '[0]'
        }
        response = self.client.post('/convert-to-pdf', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'Invalid file type')

    def test_convert_to_pdf_file_too_large(self):
        # Create a file that is 10MB + 1 byte
        file_size = (10 * 1024 * 1024) + 1
        data = b'0' * file_size
        
        # Create temporary file
        filename = os.path.join(self.uploads_dir, 'large_file.jpg')
        try:
            with open(filename, 'wb') as f:
                f.write(data)
            
            # Open the file for the request
            with open(filename, 'rb') as f:
                data = {
                    'files': [(f, 'large_file.jpg')],
                    'order': '[0]'
                }
                response = self.client.post('/convert-to-pdf', data=data, content_type='multipart/form-data')
                
                self.assertEqual(response.status_code, 413)
                json_data = response.get_json()
                self.assertEqual(json_data['error'], 'Individual file size exceeds limit')
        finally:
            # Clean up the test file
            if os.path.exists(filename):
                os.remove(filename)

    def test_convert_to_pdf_total_size_too_large(self):
        # Create multiple files that together exceed 50MB
        file_size = 5 * 1024 * 1024  # 5MB per file
        data = b'0' * file_size
        
        # Create temporary files
        test_files = []
        file_handles = []
        try:
            # Create test files
            for i in range(11):  # 11 files * 5MB = 55MB total
                filename = os.path.join(self.uploads_dir, f'test_large_file_{i}.jpg')
                with open(filename, 'wb') as f:
                    f.write(data)
                test_files.append(filename)
            
            # Prepare data for request
            data = MultiDict([
                ('order', '[' + ','.join(str(i) for i in range(11)) + ']')
            ])
            
            # Add files to data
            for i, filename in enumerate(test_files):
                f = open(filename, 'rb')
                file_handles.append(f)
                file_storage = FileStorage(
                    stream=f,
                    filename=f'test_large_file_{i}.jpg',
                    content_type='image/jpeg'
                )
                data.add('files', file_storage)
            
            # Make the request
            response = self.client.post('/convert-to-pdf',
                                      data=data,
                                      content_type='multipart/form-data')
            
            self.assertEqual(response.status_code, 413)
            json_data = response.get_json()
            self.assertEqual(json_data['error'], 'Total file size exceeds limit')
        finally:
            # Close all file handles
            for f in file_handles:
                f.close()
            
            # Clean up test files
            for filename in test_files:
                if os.path.exists(filename):
                    os.remove(filename)

    def test_convert_to_pdf_success(self):
        data = {
            'files': [(img, f'test_{i}.jpg') for i, img in enumerate(self.test_images)],
            'order': '[0,1]'
        }
        response = self.client.post('/convert-to-pdf', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        
        json_data = response.get_json()
        self.assertIn('download_url', json_data)
        self.assertIn('file_size', json_data)
        self.assertIn('page_count', json_data)
        self.assertEqual(json_data['page_count'], 2)
        
        # Verify the PDF file exists
        pdf_path = os.path.join(self.uploads_dir, os.path.basename(json_data['download_url']))
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(os.path.getsize(pdf_path) > 0)

    def test_convert_to_pdf_with_invalid_order(self):
        data = {
            'files': [(img, f'test_{i}.jpg') for i, img in enumerate(self.test_images)],
            'order': '[0,2]'  # Invalid index 2
        }
        response = self.client.post('/convert-to-pdf', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'Invalid image order')

if __name__ == '__main__':
    unittest.main() 