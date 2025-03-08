"""
Metrics and visualization module for FileSense.
This module handles analytics data processing, CSV generation, and data visualization.
"""
import os
import csv
import pandas as pd

class MetricsAnalyzer:
    def __init__(self):
        self.analytics_file = 'analytics.csv'
        
    def analyze_performance_data(self, file_list, start_time=None, dry_run=False):
        """
        Analyze performance data and compute file statistics.
        
        Args:
            file_list (List): List of file paths to analyze
            start_time (float): Start time of analysis (optional)
            dry_run (bool): Whether this is a dry run
            
        Returns:
            Dict: Performance data with file statistics
        """
        try:
            import time
            current_time = time.time()
            
            # Initialize counters
            N = len(file_list)
            img_num = 0
            doc_num = 0
            uncat_num = 0
            image_size = 0
            doc_size = 0
            uncat_size = 0
            
            # Track file grouping
            grouped_files = {
                'images': [],
                'documents': [],
                'unclassified': []
            }
            
            # Process each file
            for file_path in file_list:
                try:
                    file_size = os.path.getsize(file_path)
                    ext = os.path.splitext(file_path)[1].lower()
                    
                    # Categorize files
                    if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        img_num += 1
                        image_size += file_size
                        grouped_files['images'].append(file_path)
                    elif ext in ['.pdf', '.docx', '.doc', '.txt', '.csv']:
                        doc_num += 1
                        doc_size += file_size
                        grouped_files['documents'].append(file_path)
                    else:
                        uncat_num += 1
                        uncat_size += file_size
                        grouped_files['unclassified'].append(file_path)
                        
                except OSError:
                    uncat_num += 1
                    grouped_files['unclassified'].append(file_path)
            
            # Calculate time taken if start_time was provided
            time_taken = round(current_time - start_time, 2) if start_time else 0
            
            return {
                "total_files": N,
                "#image_files": img_num,
                "image_size(B)": image_size,
                "#document_files": doc_num,
                "document_size(B)": doc_size,
                "#unclassified_files": uncat_num,
                "unclassified_size(B)": uncat_size,
                "time_taken(s)": time_taken,
                "dry_run": dry_run,
                "grouped_files": grouped_files,
                "directories_created": 0,
                "files_moved": 0
            }
            
        except Exception as e:
            print(f"Error analyzing performance data: {str(e)}")
            return {}

    def process_analysis_results(self, result):
        """
        Process analysis results and prepare analytics data.
        
        Args:
            result (dict): Analysis results from file organization
            
        Returns:
            dict: Processed analytics data
        """
        return {
            'total_files': result['performance_data'].get('total_files', 0),
            'image_files': result['performance_data'].get('#image_files', 0),
            'image_size_bytes': result['performance_data'].get('image_size(B)', 0),
            'document_files': result['performance_data'].get('#document_files', 0),
            'document_size_bytes': result['performance_data'].get('document_size(B)', 0),
            'unclassified_files': result['performance_data'].get('#unclassified_files', 0),
            'unclassified_size_bytes': result['performance_data'].get('unclassified_size(B)', 0),
            'analysis_time': result['performance_data'].get('time_taken(s)', 0),
            'num_categories': len(result['proposed_struct']),
            'categories': ', '.join(sorted(result['proposed_struct'].keys())),
            'directories_to_create': len(result['proposed_struct']),
            'files_to_move': sum(len(files) for files in result['proposed_struct'].values()),
            'errors': result.get('errors', 'None')
        }

    def write_analytics_to_csv(self, analysis_results):
        """
        Write analysis results to a CSV file.
        
        Args:
            analysis_results (Dict): Dictionary containing analysis results
        """
        try:
            # Extract categories and their data
            categories = analysis_results.get('categories', '').split(', ')
            category_data = [{
                'Category': cat,
                'File_Count': int(analysis_results.get(f'{cat}_files', 0)),
                'Size_Bytes': int(analysis_results.get(f'{cat}_size_bytes', 0))
            } for cat in categories]
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(category_data)
            df.to_csv(self.analytics_file, index=False)
            
        except Exception as e:
            print(f"Error writing analytics: {str(e)}")
            # Fallback to simple CSV writing
            with open(self.analytics_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Attribute', 'Value'])
                for key, value in analysis_results.items():
                    writer.writerow([key, value])

    def generate_visualization(self, analysis_results):
        """
        Generate visualization from analysis results.
        This function is currently disabled but can be enabled for visualization needs.
        
        Args:
            analysis_results (Dict): Dictionary containing analysis results
        """
        """
        try:
            import matplotlib.pyplot as plt
            
            # Extract categories and their data
            categories = analysis_results.get('categories', '').split(', ')
            category_data = [{
                'Category': cat,
                'File_Count': int(analysis_results.get(f'{cat}_files', 0)),
            } for cat in categories]
            
            df = pd.DataFrame(category_data)
            
            plt.figure(figsize=(10, 8))
            plt.pie(df['File_Count'], labels=df['Category'], autopct='%1.1f%%')
            plt.title('File Distribution by Category')
            plt.savefig('category_distribution.png')
            plt.close()
            
        except Exception as e:
            print(f"Error generating visualization: {str(e)}")
        """
        pass
