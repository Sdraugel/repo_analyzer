# web_page_generator.py

import os

class WebPageGenerator:
    def __init__(self, directory="system_pages"):
        self.directory = directory
        self.create_directory()

    def create_directory(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def create_main_overview_page(self, selected_groups):
        table_rows = ""

        for i, group in enumerate(selected_groups):
            group_name = group.replace(' ', '_')
            group_page = f"group_{i+1}.html"
            table_rows += f"""
            <tr>
                <td>{group}</td>
                <td><a href="{group_page}" target="_self"><button>View {group}</button></a></td>
            </tr>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Main Overview</title>
            <style>
                table {{
                    width: 50%;
                    margin: 50px auto;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                button {{
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
            </style>
        </head>
        <body>
            <h2 style="text-align: center;">System Overview</h2>
            <table>
                <thead>
                    <tr>
                        <th>Group Name</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </body>
        </html>
        """

        main_file = os.path.join(self.directory, "index.html")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Main overview page saved to {main_file}")

    def create_group_pages(self, grouped_files, selected_groups):
        for i, group in enumerate(selected_groups):
            group_name = group.replace(' ', '_')
            group_page = f"group_{i+1}.html"
            file_rows = ""

            for file_info in grouped_files[group]:
                file_name = os.path.basename(file_info['filename'])
                file_detail_page = f"{group_name}_{file_name}.html"
                file_rows += f"""
                <tr>
                    <td>{file_name}</td>
                    <td><a href="{file_detail_page}" target="_self"><button>View Details</button></a></td>
                </tr>
                """

                # Create the file detail page
                self.create_file_detail_page(file_name, file_info['description'], file_detail_page)

            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{group} Overview</title>
                <style>
                    table {{
                        width: 60%;
                        margin: 50px auto;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        padding: 15px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                    button {{
                        padding: 10px 20px;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        cursor: pointer;
                    }}
                    button:hover {{
                        background-color: #45a049;
                    }}
                </style>
            </head>
            <body>
                <h2 style="text-align: center;">{group} Files</h2>
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {file_rows}
                    </tbody>
                </table>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="index.html"><button>Back to Main Overview</button></a>
                </div>
            </body>
            </html>
            """

            group_file = os.path.join(self.directory, group_page)
            with open(group_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Group page for {group} saved to {group_file}")

    def create_file_detail_page(self, file_name, description, file_detail_page):
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{file_name} Details</title>
            <style>
                .container {{
                    width: 60%;
                    margin: 50px auto;
                }}
                h2 {{
                    text-align: center;
                }}
                .description {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                button {{
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>{file_name}</h2>
                <div class="description">
                    <p><strong>Description:</strong></p>
                    <p>{description}</p>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="javascript:history.back()"><button>Back</button></a>
                </div>
            </div>
        </body>
        </html>
        """

        file_page = os.path.join(self.directory, file_detail_page)
        with open(file_page, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Detail page for {file_name} saved to {file_page}")

    def save_all_pages(self, grouped_files, selected_groups):
        self.create_group_pages(grouped_files, selected_groups)
        self.create_main_overview_page(selected_groups)
