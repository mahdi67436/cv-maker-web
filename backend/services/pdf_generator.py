"""
PDF Generator Service
======================
Generate PDF files from resume data.
"""

import os
from flask import current_app
from datetime import datetime


class PDFGenerator:
    """Service for generating PDF resumes."""

    def __init__(self):
        self.export_folder = current_app.config.get('EXPORT_FOLDER', 'exports')

    def generate(self, resume_data, template='modern', custom_styles=None):
        """Generate PDF from resume data."""
        try:
            # Generate HTML first
            html_content = self._generate_html(resume_data, template, custom_styles)
            
            # Convert to PDF using WeasyPrint
            from weasyprint import HTML, CSS
            
            # Create export directory if needed
            os.makedirs(self.export_folder, exist_ok=True)
            
            # Generate filename
            filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.export_folder, filename)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(filepath)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath
            }
            
        except Exception as e:
            import logging
            logging.error(f"PDF generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_html(self, resume_data, template, custom_styles=None):
        """Generate HTML content for PDF."""
        template_configs = {
            'modern': self._modern_template,
            'professional': self._professional_template,
            'creative': self._creative_template,
            'ats': self._ats_template,
            'dark': self._dark_template
        }
        
        template_func = template_configs.get(template, self._modern_template)
        
        return template_func(resume_data, custom_styles)

    def _modern_template(self, resume_data, custom_styles):
        """Modern template HTML."""
        styles = """
        <style>
            @page { margin: 0.5in; }
            body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }
            .header { text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; }
            .name { font-size: 28pt; font-weight: bold; color: #1e40af; margin: 0; }
            .title { font-size: 14pt; color: #64748b; margin-top: 5px; }
            .contact { font-size: 10pt; color: #64748b; margin-top: 8px; }
            .section { margin-bottom: 15px; }
            .section-title { font-size: 14pt; font-weight: bold; color: #2563eb; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-bottom: 10px; }
            .experience-item, .education-item { margin-bottom: 12px; }
            .item-header { display: flex; justify-content: space-between; align-items: baseline; }
            .item-title { font-weight: bold; font-size: 11pt; }
            .item-subtitle { font-style: italic; color: #64748b; }
            .item-date { font-size: 10pt; color: #64748b; }
            .item-description { font-size: 10pt; margin-top: 4px; }
            .skills-list { display: flex; flex-wrap: wrap; gap: 5px; }
            .skill-tag { background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-size: 10pt; }
            .two-column { display: flex; gap: 30px; }
            .column { flex: 1; }
        </style>
        """
        
        return self._base_html(resume_data, styles)

    def _professional_template(self, resume_data, custom_styles):
        """Professional template HTML."""
        styles = """
        <style>
            @page { margin: 0.5in; }
            body { font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.6; color: #000; }
            .header { text-align: center; border-bottom: 3px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
            .name { font-size: 24pt; font-weight: bold; text-transform: uppercase; margin: 0; }
            .contact { font-size: 10pt; margin-top: 8px; }
            .section { margin-bottom: 18px; }
            .section-title { font-size: 14pt; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #000; padding-bottom: 3px; margin-bottom: 12px; }
            .experience-item, .education-item { margin-bottom: 15px; }
            .item-header { display: flex; justify-content: space-between; }
            .item-title { font-weight: bold; }
            .item-subtitle { font-style: italic; }
            .item-description { text-align: justify; margin-top: 5px; }
        </style>
        """
        
        return self._base_html(resume_data, styles)

    def _creative_template(self, resume_data, custom_styles):
        """Creative template HTML."""
        styles = """
        <style>
            @page { margin: 0.5in; }
            body { font-family: 'Verdana', sans-serif; font-size: 11pt; line-height: 1.5; color: #333; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; }
            .name { font-size: 32pt; font-weight: bold; margin: 0; }
            .title { font-size: 14pt; opacity: 0.9; margin-top: 5px; }
            .contact { font-size: 10pt; opacity: 0.9; margin-top: 10px; }
            .section { margin-bottom: 18px; }
            .section-title { font-size: 16pt; font-weight: bold; color: #764ba2; margin-bottom: 12px; }
            .experience-item, .education-item { background: #f8f9fa; padding: 12px; border-radius: 6px; margin-bottom: 10px; }
            .item-title { font-weight: bold; color: #667eea; }
            .item-subtitle { color: #666; }
            .item-date { float: right; font-size: 9pt; color: #999; }
        </style>
        """
        
        return self._base_html(resume_data, styles)

    def _ats_template(self, resume_data, custom_styles):
        """ATS-optimized template HTML."""
        styles = """
        <style>
            @page { margin: 0.75in; }
            body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.4; color: #000; }
            .header { text-align: center; margin-bottom: 20px; }
            .name { font-size: 22pt; font-weight: bold; }
            .title { font-size: 12pt; margin-top: 5px; }
            .contact { font-size: 10pt; margin-top: 5px; }
            .section { margin-bottom: 15px; page-break-inside: avoid; }
            .section-title { font-size: 14pt; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }
            .item-header { margin-bottom: 5px; }
            .item-title { font-weight: bold; }
            .item-subtitle { font-style: italic; }
            .item-date { float: right; }
            .item-description { margin-top: 3px; }
            table { width: 100%; border-collapse: collapse; }
            td { padding: 3px 0; }
        </style>
        """
        
        return self._base_html(resume_data, styles)

    def _dark_template(self, resume_data, custom_styles):
        """Dark theme template HTML."""
        styles = """
        <style>
            @page { margin: 0.5in; }
            body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #e2e8f0; background: #1e293b; padding: 20px; }
            .header { text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 15px; margin-bottom: 20px; }
            .name { font-size: 28pt; font-weight: bold; color: #f8fafc; margin: 0; }
            .title { font-size: 14pt; color: #94a3b8; margin-top: 5px; }
            .contact { font-size: 10pt; color: #94a3b8; margin-top: 8px; }
            .section { margin-bottom: 15px; }
            .section-title { font-size: 14pt; font-weight: bold; color: #3b82f6; border-bottom: 1px solid #334155; padding-bottom: 5px; margin-bottom: 10px; }
            .experience-item, .education-item { margin-bottom: 12px; }
            .item-title { font-weight: bold; color: #f8fafc; }
            .item-subtitle { color: #94a3b8; font-style: italic; }
            .item-date { font-size: 10pt; color: #64748b; }
            .item-description { color: #cbd5e1; margin-top: 4px; }
            .skill-tag { background: #334155; padding: 3px 8px; border-radius: 4px; font-size: 10pt; color: #e2e8f0; }
        </style>
        """
        
        return self._base_html(resume_data, styles)

    def _base_html(self, resume_data, styles):
        """Generate base HTML structure."""
        name = resume_data.get('full_name', 'Your Name')
        title = resume_data.get('title', 'Professional Title')
        
        # Contact info
        contact_parts = []
        if resume_data.get('email'):
            contact_parts.append(resume_data['email'])
        if resume_data.get('phone'):
            contact_parts.append(resume_data['phone'])
        if resume_data.get('city'):
            contact_parts.append(resume_data['city'])
        if resume_data.get('country'):
            contact_parts.append(resume_data['country'])
        
        contact = ' | '.join(contact_parts)
        
        # Social links
        social_parts = []
        if resume_data.get('linkedin'):
            social_parts.append(f"LinkedIn: {resume_data['linkedin']}")
        if resume_data.get('github'):
            social_parts.append(f"GitHub: {resume_data['github']}")
        if resume_data.get('portfolio'):
            social_parts.append(f"Portfolio: {resume_data['portfolio']}")
        
        social = ' | '.join(social_parts) if social_parts else ''
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{name} - Resume</title>
            {styles}
        </head>
        <body>
            <div class="header">
                <h1 class="name">{name}</h1>
                <p class="title">{title}</p>
                <p class="contact">{contact}</p>
                {f'<p class="contact">{social}</p>' if social else ''}
            </div>
        """
        
        # Summary
        if resume_data.get('summary'):
            html += f"""
            <div class="section">
                <h2 class="section-title">Professional Summary</h2>
                <p>{resume_data['summary']}</p>
            </div>
            """
        
        # Experience
        experiences = resume_data.get('experiences', [])
        if experiences:
            html += """
            <div class="section">
                <h2 class="section-title">Work Experience</h2>
            """
            for exp in experiences:
                html += f"""
                <div class="experience-item">
                    <div class="item-header">
                        <span class="item-title">{exp.get('position', '')}</span>
                        <span class="item-date">{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}</span>
                    </div>
                    <div class="item-subtitle">{exp.get('company', '')}</div>
                    <div class="item-description">{exp.get('description', '')}</div>
                </div>
                """
            html += "</div>"
        
        # Education
        education = resume_data.get('education', [])
        if education:
            html += """
            <div class="section">
                <h2 class="section-title">Education</h2>
            """
            for edu in education:
                html += f"""
                <div class="education-item">
                    <div class="item-header">
                        <span class="item-title">{edu.get('degree', '')}</span>
                        <span class="item-date">{edu.get('start_date', '')} - {edu.get('end_date', '')}</span>
                    </div>
                    <div class="item-subtitle">{edu.get('institution', '')}</div>
                    {f'<div class="item-description">{edu.get("description", "")}</div>' if edu.get('description') else ''}
                </div>
                """
            html += "</div>"
        
        # Skills
        skills = resume_data.get('skills', [])
        if skills:
            html += """
            <div class="section">
                <h2 class="section-title">Skills</h2>
                <div class="skills-list">
            """
            for skill in skills:
                level = skill.get('level', '')
                html += f'<span class="skill-tag">{skill.get("name", "")}{f" ({level})" if level else ""}</span>'
            html += """
                </div>
            </div>
            """
        
        # Projects
        projects = resume_data.get('projects', [])
        if projects:
            html += """
            <div class="section">
                <h2 class="section-title">Projects</h2>
            """
            for proj in projects:
                html += f"""
                <div class="experience-item">
                    <div class="item-title">{proj.get('name', '')}</div>
                    <div class="item-description">{proj.get('description', '')}</div>
                    {f'<div class="item-subtitle">{proj.get("technologies", "")}</div>' if proj.get('technologies') else ''}
                </div>
                """
            html += "</div>"
        
        # Certifications
        certifications = resume_data.get('certifications', [])
        if certifications:
            html += """
            <div class="section">
                <h2 class="section-title">Certifications</h2>
            """
            for cert in certifications:
                html += f"""
                <div class="experience-item">
                    <div class="item-header">
                        <span class="item-title">{cert.get('name', '')}</span>
                        <span class="item-date">{cert.get('issue_date', '')}</span>
                    </div>
                    <div class="item-subtitle">{cert.get('issuing_organization', '')}</div>
                </div>
                """
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
