import json
import os
import openai
import tkinter as tk

def analyze_qpid_usage(data, progress_var, progress_label, log_box, stop_processing):
    qpid_descriptions = []
    total_entries = len(data)
    
    for i, entry in enumerate(data):
        if stop_processing:
            break
        
        if 'qpid' in entry['description'].lower():
            qpid_descriptions.append(entry)
        
        progress_var.set((i + 1) / total_entries * 100)
        progress_label.config(text=f"Analyzing Qpid Usage... ({i + 1}/{total_entries})")
        log_box.insert(tk.END, f"Scanned {i + 1}/{total_entries} entries for Qpid.\n")
        log_box.see(tk.END)
    
    if qpid_descriptions:
        combined_text = "\n\n".join([desc['description'] for desc in qpid_descriptions])
        
        progress_label.config(text="Qpid Analysis Complete. Generating summary file...")
        log_box.insert(tk.END, "Qpid Analysis Complete. Generating summary file...\n")
        log_box.see(tk.END)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in analyzing and summarizing text."},
                {"role": "user", "content": f"Please summarize the usage of 'qpid' in the following descriptions:\n\n{combined_text}"}
            ]
        )
        summary = response.choices[0].message['content']
        
        log_box.insert(tk.END, "Summary of Qpid Usage:\n" + summary + "\n\n")
        log_box.see(tk.END)
        
        output_file_path = os.path.join('analysis_files', 'qpid_usage_summary.json')
        with open(output_file_path, 'w') as output_file:
            json.dump({"summary": summary, "details": qpid_descriptions}, output_file, indent=4)
        
        log_box.insert(tk.END, f"Qpid usage summary saved to {output_file_path}\n")
        log_box.see(tk.END)
        
        progress_var.set(100)
        progress_label.config(text="Analysis complete. All tasks finished.")
        
        return summary
    else:
        log_box.insert(tk.END, "No instances of 'qpid' found in the descriptions.\n")
        log_box.see(tk.END)
        progress_var.set(100)
        progress_label.config(text="Analysis complete. No Qpid instances found.")
        return "No instances of 'qpid' found in the descriptions."
