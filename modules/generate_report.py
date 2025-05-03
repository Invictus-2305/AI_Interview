# from fpdf import FPDF
# import matplotlib.pyplot as plt
# from io import BytesIO
# import numpy as np
# import pandas as pd
# from modules.evaluate import evaluate

# class PDFReport(FPDF):
#     def header(self):
#         self.set_font('Arial', 'B', 12)
#         self.cell(0,10, 'AI Evaluation Report' ,0 , 1, 'C')
    
#     def footer(self):
#         self.set_y(-15)
#         self.set_font('Arial', 'I', 8)
#         self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

#     def add_spider_chart(self, scores, title):
#         categories = ['Technical', 'Clarity', 'Relevance', 'Depth']
#         N = len(categories)

#         angles = [n / float(N) * 2 * np.pi for n in range(N)]
#         angles += angles[:1]
        
#         fig = plt.figure(figsize=(6, 6))
#         ax = fig.add_subplot(111, polar=True)

#         ax.set_theta_offset(np.pi / 2)
#         ax.set_theta_direction(-1)
        
#         plt.xticks(angles[:-1], categories)
#         ax.set_rlabel_position(0)
#         plt.yticks([2,4,6,8,10], ["2","4","6","8","10"], color="grey", size=7)
#         plt.ylim(0, 10)
        
#         values = scores[:4]  
#         values += values[:1]
#         ax.plot(angles, values, linewidth=1, linestyle='solid')
#         ax.fill(angles, values, 'b', alpha=0.1)
        
#         plt.title(title, size=11, y=1.1)
        
#         # Save to buffer and add to PDF
#         img_buffer = BytesIO()
#         plt.savefig(img_buffer, format='png', dpi=100)
#         plt.close()
        
#         self.image(img_buffer, x=50, w=100)
#         img_buffer.close()


# def generate_report(df):
#     pdf = PDFReport()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
    
#     # Filter out questions without responses
#     answered_questions = df[(df['Type'] == 'Question') & (df['User Response'].notna())]
    
#     if len(answered_questions) == 0:
#         pdf.cell(0, 10, "No answered questions to evaluate", ln=1)
#         pdf.output("interview_report.pdf")
#         return "interview_report.pdf"

    
#     pdf.cell(0, 10, "Overall Evaluation", ln=1, align='C')
  
#     evaluations = []
#     for _, row in df[df['Type'] == 'Question'].iterrows():
#         if row['User Response']:
#             eval_result = evaluate(row['Content'], row['User Response'])
#             evaluations.append(eval_result)
    
#     if evaluations:
#         avg_scores = {
#             'technical': sum(e['technical_score'] for e in evaluations) / len(evaluations),
#             'clarity': sum(e['clarity_score'] for e in evaluations) / len(evaluations),
#             'relevance': sum(e['relevance_score'] for e in evaluations) / len(evaluations),
#             'depth': sum(e['depth_score'] for e in evaluations) / len(evaluations),
#             'overall': sum(e['overall_score'] for e in evaluations) / len(evaluations)
#         }
        
#         # Add spider chart
#         pdf.add_spider_chart([
#             avg_scores['technical'],
#             avg_scores['clarity'],
#             avg_scores['relevance'],
#             avg_scores['depth']
#         ], "Average Performance Metrics")
        
#         # Add overall score
#         pdf.ln(85)
#         pdf.cell(0, 10, f"Overall Score: {avg_scores['overall']:.1f}/10", ln=1, align='C')
    

#     pdf.add_page()
#     pdf.cell(0, 10, "Detailed Question Evaluation", ln=1, align='C')
    
#     for index, row in df.iterrows():
#         if row['Type'] == 'Question' and row['User Response']:
#             pdf.set_font('Arial', 'B', 12)
#             pdf.multi_cell(0, 10, f"Question {index}: {row['Content']}")
#             pdf.set_font('Arial', '', 11)
#             pdf.multi_cell(0, 10, f"Response: {row['User Response']}")
            
#             evaluation = evaluate(row['Content'], row['User Response'])
            
#             # Add evaluation metrics
#             pdf.set_font('Arial', 'B', 11)
#             pdf.cell(0, 10, "Evaluation:", ln=1)
#             pdf.set_font('Arial', '', 10)
#             pdf.multi_cell(0, 8, f"Technical: {evaluation['technical_score']}/10")
#             pdf.multi_cell(0, 8, f"Clarity: {evaluation['clarity_score']}/10")
#             pdf.multi_cell(0, 8, f"Relevance: {evaluation['relevance_score']}/10")
#             pdf.multi_cell(0, 8, f"Depth: {evaluation['depth_score']}/10")
#             pdf.multi_cell(0, 8, f"Overall: {evaluation['overall_score']}/10")
            
#             # Add feedback
#             pdf.set_font('Arial', 'B', 11)
#             pdf.cell(0, 10, "Feedback:", ln=1)
#             pdf.set_font('Arial', '', 10)
#             pdf.multi_cell(0, 8, evaluation['feedback'])
            
#             if evaluation['overall_score'] < 7 and evaluation.get('expected_response'):
#                 pdf.set_font('Arial', 'B', 11)
#                 pdf.cell(0, 10, "Suggested Improvement:", ln=1)
#                 pdf.set_font('Arial', '', 10)
#                 pdf.multi_cell(0, 8, evaluation['expected_response'])
            
#             pdf.ln(5)
    
#     # Save the PDF
#     report_path = "interview_report.pdf"
#     pdf.output(report_path)
#     return report_path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import numpy as np
import pandas as pd
from modules.evaluate import evaluate
import unicodedata
import os

def sanitize_text(text):
    """Replace unsupported Unicode characters with closest ASCII."""
    if not text:
        return ""
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text

class PDFReport(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(True, margin=15)
        self.set_font('Arial', '', 12)  # Built-in Arial font
    
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'AI Evaluation Report', 0, 1, 'C')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_spider_chart(self, scores, title):
        categories = ['Technical', 'Clarity', 'Relevance', 'Depth']
        N = len(categories)

        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, polar=True)

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        plt.xticks(angles[:-1], categories)
        ax.set_rlabel_position(0)
        plt.yticks([2,4,6,8,10], ["2","4","6","8","10"], color="grey", size=7)
        plt.ylim(0, 10)
        
        values = scores[:4]  
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid')
        ax.fill(angles, values, 'b', alpha=0.1)
        
        plt.title(title, size=11, y=1.1)
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        plt.close()
        
        self.image(img_buffer, x=50, w=100)
        img_buffer.close()

def generate_report(df):
    pdf = PDFReport()
    pdf.add_page()
    
    default_eval = {
        'technical_score': 0,
        'clarity_score': 0,
        'relevance_score': 0,
        'depth_score': 0,
        'overall_score': 0,
        'feedback': 'Evaluation not available',
        'expected_response': ''
    }
    
    evaluations = []
    for _, row in df[df['Type'] == 'Question'].iterrows():
        if pd.notna(row['User Response']):
            try:
                eval_result = evaluate(row['Content'], row['User Response'])
                if isinstance(eval_result, dict):
                    evaluations.append(eval_result)
                else:
                    evaluations.append(default_eval)
            except Exception as e:
                print(f"Evaluation error: {e}")
                evaluations.append(default_eval)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Overall Evaluation', 0, 1, 'C')
    pdf.ln(5)
    
    if evaluations:
        avg_scores = {
            'technical': sum(e['technical_score'] for e in evaluations) / len(evaluations),
            'clarity': sum(e['clarity_score'] for e in evaluations) / len(evaluations),
            'relevance': sum(e['relevance_score'] for e in evaluations) / len(evaluations),
            'depth': sum(e['depth_score'] for e in evaluations) / len(evaluations),
            'overall': sum(e['overall_score'] for e in evaluations) / len(evaluations)
        }
        
        pdf.add_spider_chart([
            avg_scores['technical'],
            avg_scores['clarity'],
            avg_scores['relevance'],
            avg_scores['depth']
        ], "Average Performance Metrics")
        
        pdf.ln(85)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Overall Score: {avg_scores['overall']:.1f}/10", 0, 1, 'C')
    
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Detailed Questions and Responses', 0, 1, 'C')
    pdf.ln(5)
    
    for index, row in df.iterrows():
        if row['Type'] == 'Question' and pd.notna(row['User Response']):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Question {index}:", 0, 1)
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 5, sanitize_text(row['Content']))
            pdf.ln(2)
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "Response:", 0, 1)
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 5, sanitize_text(row['User Response']))
            pdf.ln(2)
            
            eval_result = evaluations[index - 1] if (index - 1) < len(evaluations) else default_eval
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "Evaluation:", 0, 1)
            pdf.set_font('Arial', '', 11)
            pdf.cell(0, 5, f"Technical: {eval_result['technical_score']}/10", 0, 1)
            pdf.cell(0, 5, f"Clarity: {eval_result['clarity_score']}/10", 0, 1)
            pdf.cell(0, 5, f"Relevance: {eval_result['relevance_score']}/10", 0, 1)
            pdf.cell(0, 5, f"Depth: {eval_result['depth_score']}/10", 0, 1)
            pdf.cell(0, 5, f"Overall: {eval_result['overall_score']}/10", 0, 1)
            pdf.ln(2)
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "Feedback:", 0, 1)
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 5, sanitize_text(eval_result['feedback']))
            pdf.ln(2)
            
            if eval_result['overall_score'] < 7 and eval_result.get('expected_response'):
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "Suggested Improvement:", 0, 1)
                pdf.set_font('Arial', '', 11)
                pdf.multi_cell(0, 5, sanitize_text(eval_result['expected_response']))
            
            pdf.ln(10)

    report_path = "interview_report.pdf"
    pdf.output(report_path)
    return report_path
