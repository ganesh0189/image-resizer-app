import unittest
import os
import sys
from datetime import datetime

def run_tests():
    # Add the project root directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Create a test runner with verbosity
    test_runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    start_time = datetime.now()
    result = test_runner.run(test_suite)
    end_time = datetime.now()
    
    # Generate test report
    generate_test_report(result, start_time, end_time)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

def generate_test_report(result, start_time, end_time):
    # Create reports directory if it doesn't exist
    os.makedirs('test_reports', exist_ok=True)
    
    # Generate report filename with timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_filename = f'test_reports/test_report_{timestamp}.txt'
    
    with open(report_filename, 'w') as f:
        f.write(f"Test Report - {timestamp}\n")
        f.write("=" * 50 + "\n\n")
        
        # Write test summary
        f.write(f"Total Tests Run: {result.testsRun}\n")
        f.write(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}\n")
        f.write(f"Failed: {len(result.failures)}\n")
        f.write(f"Errors: {len(result.errors)}\n")
        f.write(f"Run Time: {end_time - start_time}\n\n")
        
        # Write detailed results
        if result.failures:
            f.write("Failed Tests:\n")
            f.write("-" * 20 + "\n")
            for failure in result.failures:
                f.write(f"{failure[0]}\n")
                f.write(f"{failure[1]}\n\n")
        
        if result.errors:
            f.write("Errors:\n")
            f.write("-" * 20 + "\n")
            for error in result.errors:
                f.write(f"{error[0]}\n")
                f.write(f"{error[1]}\n\n")
    
    print(f"\nTest report generated: {report_filename}")

if __name__ == '__main__':
    sys.exit(run_tests()) 