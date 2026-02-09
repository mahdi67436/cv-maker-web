"""
AI Writer Service
=================
AI-powered content generation for resumes.
"""

import re
from flask import current_app


class AIWriter:
    """Service for AI-powered resume content generation."""

    def __init__(self):
        self.api_key = current_app.config.get('AI_API_KEY')
        self.model = current_app.config.get('AI_MODEL', 'gpt-4')

    def generate_summary(self, name, experience, skills, job_description=''):
        """Generate professional summary."""
        try:
            if not self.api_key:
                # Return template-based summary without AI
                return self._generate_template_summary(name, experience, skills, job_description)
            
            # Use AI for generation
            prompt = self._build_summary_prompt(name, experience, skills, job_description)
            response = self._call_ai(prompt)
            
            return {
                'success': True,
                'content': response.strip(),
                'suggestions': []
            }
            
        except Exception as e:
            import logging
            logging.error(f"AI summary generation error: {e}")
            return self._generate_template_summary(name, experience, skills, job_description)

    def generate_experience_description(self, company, position, achievements):
        """Generate experience bullet points."""
        try:
            if not self.api_key:
                return self._generate_template_experience(company, position, achievements)
            
            prompt = f"""
Generate professional achievement descriptions for:
Company: {company}
Position: {position}
Achievements to highlight: {', '.join(achievements) if achievements else 'General responsibilities'}

Write 3-5 bullet points using action verbs and quantify results where possible.
Format each point starting with a strong action verb.
"""
            response = self._call_ai(prompt)
            bullets = [b.strip() for b in response.strip().split('\n') if b.strip()]
            
            return {
                'success': True,
                'content': response.strip(),
                'suggestions': bullets
            }
            
        except Exception as e:
            import logging
            logging.error(f"AI experience generation error: {e}")
            return self._generate_template_experience(company, position, achievements)

    def suggest_skills(self, job_title, industry):
        """Suggest relevant skills based on job title and industry."""
        try:
            if not self.api_key:
                return self._get_template_skills(job_title, industry)
            
            prompt = f"""
Suggest 15-20 relevant skills for a {job_title} in the {industry} industry.
Include both technical and soft skills.
Format as a comma-separated list.
"""
            response = self._call_ai(prompt)
            skills = [s.strip() for s in response.strip().split(',') if s.strip()]
            
            return {
                'success': True,
                'content': response.strip(),
                'suggestions': skills
            }
            
        except Exception as e:
            import logging
            logging.error(f"AI skills suggestion error: {e}")
            return self._get_template_skills(job_title, industry)

    def improve_content(self, content, content_type, job_description=''):
        """Improve existing resume content."""
        try:
            if not self.api_key:
                return {
                    'success': True,
                    'content': content,
                    'changes': [],
                    'score': self._calculate_basic_score(content)
                }
            
            prompt = f"""
Improve the following {content_type} description for a resume.
Job context: {job_description if job_description else 'General professional role'}

Original text:
{content}

Provide an improved version that:
1. Uses strong action verbs
2. Quantifies results where possible
3. Removes filler words
4. Is concise but impactful

Return only the improved text, no explanations.
"""
            improved = self._call_ai(prompt)
            changes = self._identify_changes(content, improved)
            
            return {
                'success': True,
                'content': improved.strip(),
                'changes': changes,
                'score': self._calculate_ai_score(content, improved)
            }
            
        except Exception as e:
            import logging
            logging.error(f"AI improve content error: {e}")
            return {
                'success': True,
                'content': content,
                'changes': [],
                'score': self._calculate_basic_score(content)
            }

    def check_grammar(self, content):
        """Check grammar and spelling."""
        try:
            # Basic checks without external API
            issues = []
            words = content.split()
            
            # Check for common issues
            if len(content) < 50:
                issues.append({
                    'type': 'length',
                    'message': 'Content seems too short',
                    'severity': 'warning'
                })
            
            # Check for passive voice (basic)
            passive_patterns = [
                (r'\bwas\b', 'Consider using active voice'),
                (r'\bwere\b', 'Consider using active voice'),
                (r'\bbeen\b', 'Consider using active voice'),
                (r'\bis being\b', 'Consider using active voice'),
            ]
            
            for pattern, suggestion in passive_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    issues.append({
                        'type': 'passive_voice',
                        'message': f'Found passive voice constructions ({len(matches)} occurrences)',
                        'suggestion': suggestion,
                        'severity': 'info'
                    })
            
            # Calculate basic score
            words_count = len(words)
            sentences = re.split(r'[.!?]+', content)
            avg_sentence_length = words_count / max(len([s for s in sentences if s.strip()]), 1)
            
            score = 100
            for issue in issues:
                if issue['severity'] == 'warning':
                    score -= 10
                elif issue['severity'] == 'info':
                    score -= 3
            
            return {
                'success': True,
                'corrected': content,
                'issues': issues,
                'score': max(0, score)
            }
            
        except Exception as e:
            import logging
            logging.error(f"Grammar check error: {e}")
            return {
                'success': True,
                'corrected': content,
                'issues': [],
                'score': 50
            }

    def suggest_job_titles(self, skills, experience_years):
        """Suggest job titles based on skills and experience."""
        try:
            if not self.api_key:
                return self._get_template_job_titles(skills, experience_years)
            
            prompt = f"""
Based on the following skills and experience, suggest 5-10 job titles:
Skills: {', '.join(skills)}
Years of experience: {experience_years}

Return only job titles, one per line.
"""
            response = self._call_ai(prompt)
            titles = [t.strip() for t in response.strip().split('\n') if t.strip()]
            
            return {
                'success': True,
                'job_titles': titles
            }
            
        except Exception as e:
            import logging
            logging.error(f"Job titles suggestion error: {e}")
            return self._get_template_job_titles(skills, experience_years)

    def _call_ai(self, prompt):
        """Call AI API."""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional resume writer and career coach."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def _build_summary_prompt(self, name, experience, skills, job_description):
        """Build prompt for summary generation."""
        exp_years = len(experience) * 2 if experience else 0
        top_skills = ', '.join(skills[:5]) if skills else 'various skills'
        jd = f"Target job: {job_description}" if job_description else ""
        
        return f"""
Write a professional summary for:
Name: {name}
Experience: {exp_years} years
Key skills: {top_skills}
{jd}

The summary should:
- Be 2-3 sentences
- Highlight key achievements and skills
- Be ATS-friendly (avoid jargon)
- Sound confident but not arrogant

Return only the summary text.
"""

    def _generate_template_summary(self, name, experience, skills, job_description=''):
        """Generate template-based summary without AI."""
        exp_years = len(experience) * 2 if experience else 0
        skill_text = ', '.join(skills[:5]) if skills else 'various technologies'
        
        summary = f"Results-driven professional with {exp_years}+ years of experience "
        
        if job_description:
            summary += f"in {job_description.split()[0] if job_description else 'the field'}. "
        else:
            summary += "delivering high-quality solutions. "
        
        summary += f"Skilled in {skill_text}. "
        summary += "Committed to excellence and continuous improvement."
        
        return {
            'success': True,
            'content': summary,
            'suggestions': [
                "Add specific achievements",
                "Include metrics and numbers",
                "Tailor to job description"
            ]
        }

    def _generate_template_experience(self, company, position, achievements):
        """Generate template-based experience description."""
        bullets = [
            f"Responsible for {position} role at {company}",
            "Collaborated with cross-functional teams to achieve goals",
            "Demonstrated strong problem-solving skills"
        ]
        
        if achievements:
            bullets[0] = f"Key {position} responsibilities and achievements at {company}"
            for i, ach in enumerate(achievements[:3]):
                bullets.append(f"• {ach}")
        
        return {
            'success': True,
            'content': '\n'.join(bullets),
            'suggestions': bullets
        }

    def _get_template_skills(self, job_title, industry):
        """Get template-based skill suggestions."""
        common_skills = [
            'Communication', 'Teamwork', 'Problem Solving', 'Time Management',
            'Leadership', 'Microsoft Office', 'Google Workspace', 'Project Management',
            'Data Analysis', 'Strategic Planning', 'Customer Service', 'Adaptability'
        ]
        
        tech_skills = {
            'software': ['Python', 'JavaScript', 'SQL', 'HTML/CSS', 'Git', 'Agile', 'Scrum'],
            'data': ['Excel', 'SQL', 'Tableau', 'Power BI', 'Python', 'Statistics'],
            'marketing': ['SEO', 'Google Analytics', 'Social Media', 'Content Marketing', 'Email Marketing'],
            'design': ['Photoshop', 'Illustrator', 'Figma', 'UI/UX', 'HTML/CSS']
        }
        
        industry_skills = {
            'technology': ['Python', 'JavaScript', 'Cloud Computing', 'Machine Learning', 'DevOps'],
            'healthcare': ['Patient Care', 'Medical Terminology', 'HIPAA', 'Electronic Health Records'],
            'finance': ['Financial Analysis', 'Excel', 'Bloomberg', 'Risk Management', 'Accounting'],
            'education': ['Curriculum Development', 'Classroom Management', 'Lesson Planning', 'Assessment']
        }
        
        # Combine skills
        skills = common_skills.copy()
        skills.extend(tech_skills.get('software', []))
        
        return {
            'success': True,
            'content': ', '.join(skills[:15]),
            'suggestions': skills
        }

    def _get_template_job_titles(self, skills, experience_years):
        """Get template-based job title suggestions."""
        titles = []
        
        if experience_years < 2:
            titles = [
                'Junior Developer',
                'Entry-Level Analyst',
                'Associate',
                'Trainee',
                'Junior Consultant'
            ]
        elif experience_years < 5:
            titles = [
                'Developer',
                'Analyst',
                'Specialist',
                'Consultant',
                'Project Coordinator'
            ]
        elif experience_years < 10:
            titles = [
                'Senior Developer',
                'Lead Analyst',
                'Senior Consultant',
                'Project Manager',
                'Team Lead'
            ]
        else:
            titles = [
                'Senior Developer',
                'Lead Engineer',
                'Director',
                'Principal Consultant',
                'VP of Engineering'
            ]
        
        return {
            'success': True,
            'job_titles': titles
        }

    def _identify_changes(self, original, improved):
        """Identify changes between original and improved text."""
        changes = []
        
        if len(improved) < len(original):
            changes.append({
                'type': 'concise',
                'description': 'Made content more concise'
            })
        
        if improved.startswith('*') or improved.startswith('-'):
            changes.append({
                'type': 'formatting',
                'description': 'Added bullet point formatting'
            })
        
        action_verbs = ['Led', 'Developed', 'Managed', 'Created', 'Implemented', 'Increased']
        has_action = any(verb.lower() in improved.lower() for verb in action_verbs)
        if has_action:
            changes.append({
                'type': 'action_verbs',
                'description': 'Added strong action verbs'
            })
        
        return changes

    def _calculate_basic_score(self, content):
        """Calculate basic content score."""
        score = 50  # Base score
        
        words = content.split()
        if 50 <= len(words) <= 200:
            score += 20
        elif len(words) < 50:
            score -= 10
        
        # Check for action verbs
        action_verbs = ['achieved', 'led', 'developed', 'created', 'managed', 'increased']
        action_count = sum(1 for verb in action_verbs if verb in content.lower())
        score += min(action_count * 5, 20)
        
        # Check for numbers/metrics
        numbers = re.findall(r'\d+', content)
        if numbers:
            score += min(len(numbers) * 3, 15)
        
        return min(100, max(0, score))

    def _calculate_ai_score(self, original, improved):
        """Calculate improvement score."""
        base = self._calculate_basic_score(original)
        improvement = len(improved) / max(len(original), 1)
        
        return min(100, base + int(improvement * 20))
