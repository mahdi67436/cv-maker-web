"""
ATS Score Service
=================
ATS (Applicant Tracking System) compatibility checker.
"""

import re
from collections import Counter


class ATSScorer:
    """Service for analyzing ATS compatibility of resumes."""

    def __init__(self):
        # Common ATS keywords by category
        self.keywords = {
            'technical': [
                'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node',
                'aws', 'cloud', 'docker', 'kubernetes', 'git', 'agile', 'scrum',
                'machine learning', 'data analysis', 'excel', 'statistics',
                'project management', 'communication', 'leadership', 'problem solving'
            ],
            'soft_skills': [
                'teamwork', 'collaboration', 'communication', 'leadership',
                'problem solving', 'critical thinking', 'time management',
                'adaptability', 'creativity', 'initiative'
            ],
            'action_verbs': [
                'achieved', 'led', 'developed', 'created', 'implemented',
                'managed', 'increased', 'decreased', 'improved', 'designed',
                'organized', 'coordinated', 'analyzed', 'presented', 'trained'
            ]
        }

    def analyze_resume(self, resume, job_description=''):
        """Analyze resume for ATS compatibility."""
        try:
            # Collect resume data
            resume_data = resume.to_dict()
            
            return self.analyze_resume_data(resume_data, job_description)
            
        except Exception as e:
            import logging
            logging.error(f"ATS analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_resume_data(self, resume_data, job_description=''):
        """Analyze resume data for ATS compatibility."""
        try:
            scores = {
                'contact_info': self._check_contact_info(resume_data),
                'summary': self._check_summary(resume_data),
                'experience': self._check_experience(resume_data),
                'education': self._check_education(resume_data),
                'skills': self._check_skills(resume_data),
                'formatting': self._check_formatting(resume_data)
            }
            
            # Calculate overall score
            overall_score = sum(scores.values()) // len(scores)
            
            # Extract and analyze keywords
            keyword_analysis = self._analyze_keywords(resume_data, job_description)
            
            # Get suggestions
            suggestions = self._generate_suggestions(scores, keyword_analysis)
            
            # Get formatting issues
            formatting_issues = self._check_formatting_issues(resume_data)
            
            return {
                'success': True,
                'overall_score': overall_score,
                'section_scores': scores,
                'keywords': keyword_analysis.get('matched', []),
                'missing_keywords': keyword_analysis.get('missing', []),
                'suggestions': suggestions,
                'formatting_issues': formatting_issues,
                'keyword_analysis': keyword_analysis
            }
            
        except Exception as e:
            import logging
            logging.error(f"ATS data analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def extract_keywords(self, resume_data, job_description=''):
        """Extract and analyze keywords from resume and job description."""
        try:
            # Combine all text
            all_text = ' '.join([
                resume_data.get('summary', ''),
                resume_data.get('content', {}).get('summary', ''),
                ' '.join([e.get('description', '') for e in resume_data.get('experiences', [])]),
                ' '.join([e.get('description', '') for e in resume_data.get('education', [])]),
                ' '.join([s.get('name', '') for s in resume_data.get('skills', [])])
            ])
            
            # Extract words
            resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower()))
            
            # Job description keywords
            job_words = set()
            if job_description:
                job_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
            
            # All common keywords
            all_keywords = set()
            for category in self.keywords.values():
                all_keywords.update(category)
            
            # Find matched and missing
            matched = list(resume_words & job_words & all_keywords)
            missing = list((job_words - resume_words) & all_keywords)
            
            return {
                'success': True,
                'resume_keywords': list(resume_words & all_keywords),
                'job_keywords': list(job_words & all_keywords),
                'matched_keywords': matched,
                'missing_keywords': missing
            }
            
        except Exception as e:
            import logging
            logging.error(f"Keyword extraction error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _check_contact_info(self, resume_data):
        """Check contact information completeness."""
        score = 0
        
        if resume_data.get('email'):
            score += 25
        if resume_data.get('phone'):
            score += 25
        if resume_data.get('city') or resume_data.get('country'):
            score += 25
        if resume_data.get('full_name'):
            score += 25
        
        return score

    def _check_summary(self, resume_data):
        """Check professional summary."""
        summary = resume_data.get('summary', '')
        
        if not summary:
            return 0
        
        score = 30
        
        # Check length
        if 100 <= len(summary) <= 500:
            score += 25
        elif len(summary) > 500:
            score += 15
        
        # Check for keywords
        summary_lower = summary.lower()
        if any(kw in summary_lower for kw in self.keywords['action_verbs'][:5]):
            score += 20
        
        # Check structure
        if not summary.endswith('.'):
            score -= 10
        
        return min(100, max(0, score))

    def _check_experience(self, resume_data):
        """Check work experience section."""
        experiences = resume_data.get('experiences', resume_data.get('content', {}).get('experiences', []))
        
        if not experiences:
            return 0
        
        score = 30
        
        # Check number of experiences
        if len(experiences) >= 2:
            score += 20
        elif len(experiences) >= 1:
            score += 10
        
        # Check for descriptions
        has_descriptions = sum(1 for e in experiences if e.get('description'))
        if has_descriptions >= len(experiences) // 2:
            score += 25
        
        # Check for achievements (numbers, percentages)
        achievements_found = False
        for exp in experiences:
            desc = exp.get('description', '')
            if re.search(r'\d+%|\$\d+|\d+\s*(?:years?|months?)', desc):
                achievements_found = True
                break
        
        if achievements_found:
            score += 25
        
        return min(100, score)

    def _check_education(self, resume_data):
        """Check education section."""
        education = resume_data.get('education', resume_data.get('content', {}).get('education', []))
        
        if not education:
            return 0
        
        score = 40
        
        # Check for degree
        has_degree = any(e.get('degree') for e in education)
        if has_degree:
            score += 30
        
        # Check for institution
        has_institution = any(e.get('institution') for e in education)
        if has_institution:
            score += 20
        
        return min(100, score)

    def _check_skills(self, resume_data):
        """Check skills section."""
        skills = resume_data.get('skills', resume_data.get('content', {}).get('skills', []))
        
        if not skills:
            return 0
        
        score = 30
        
        # Check number of skills
        if len(skills) >= 10:
            score += 25
        elif len(skills) >= 5:
            score += 15
        
        # Check for categories
        has_categories = any(s.get('category') for s in skills)
        if has_categories:
            score += 20
        
        # Check for level/proficiency
        has_levels = any(s.get('level') for s in skills)
        if has_levels:
            score += 25
        
        return min(100, score)

    def _check_formatting(self, resume_data):
        """Check formatting compliance."""
        score = 100
        
        # These are harder to check from JSON data
        # This is a basic check
        
        text = str(resume_data)
        
        # Check for tables (bad for ATS)
        if 'table' in text.lower():
            score -= 30
        
        # Check for headers (good for ATS)
        if any(h in text for h in ['Experience', 'Education', 'Skills', 'Summary']):
            score += 10
        
        return min(100, max(0, score))

    def _check_formatting_issues(self, resume_data):
        """Check for specific formatting issues."""
        issues = []
        
        text = str(resume_data)
        
        # Check text length
        if len(text) < 500:
            issues.append({
                'type': 'content_length',
                'message': 'Resume content appears too short',
                'severity': 'warning'
            })
        elif len(text) > 10000:
            issues.append({
                'type': 'content_length',
                'message': 'Resume content may be too long',
                'severity': 'info'
            })
        
        # Check section headers
        required_sections = ['summary', 'experience', 'education', 'skills']
        missing_sections = []
        for section in required_sections:
            if section not in str(resume_data).lower():
                missing_sections.append(section)
        
        if missing_sections:
            issues.append({
                'type': 'missing_sections',
                'message': f'Missing sections: {", ".join(missing_sections)}',
                'severity': 'warning'
            })
        
        return issues

    def _analyze_keywords(self, resume_data, job_description):
        """Analyze keywords for ATS matching."""
        # Combine all resume text
        all_text = ' '.join([
            resume_data.get('summary', ''),
            resume_data.get('content', {}).get('summary', ''),
            ' '.join([e.get('description', '') for e in resume_data.get('experiences', [])]),
            ' '.join([s.get('name', '') for s in resume_data.get('skills', [])])
        ])
        
        resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower()))
        
        # Job description keywords
        job_words = set()
        if job_description:
            job_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
        
        # All tracked keywords
        all_keywords = set()
        for category in self.keywords.values():
            all_keywords.update(category)
        
        # Find matched and missing
        matched = list(resume_words & job_words & all_keywords)
        missing = list((job_words - resume_words) & all_keywords)
        
        # Calculate match percentage
        if job_words & all_keywords:
            match_rate = len(matched) / len(job_words & all_keywords) * 100
        else:
            match_rate = 0
        
        return {
            'matched': matched,
            'missing': missing,
            'match_rate': match_rate,
            'total_matched': len(matched),
            'total_missing': len(missing)
        }

    def _generate_suggestions(self, scores, keyword_analysis):
        """Generate improvement suggestions."""
        suggestions = []
        
        # Section-based suggestions
        if scores['contact_info'] < 75:
            suggestions.append({
                'type': 'contact_info',
                'message': 'Add missing contact information',
                'priority': 'high'
            })
        
        if scores['summary'] < 50:
            suggestions.append({
                'type': 'summary',
                'message': 'Add or improve your professional summary',
                'priority': 'high'
            })
        
        if scores['experience'] < 50:
            suggestions.append({
                'type': 'experience',
                'message': 'Add more work experience with descriptions',
                'priority': 'high'
            })
        
        if scores['skills'] < 50:
            suggestions.append({
                'type': 'skills',
                'message': 'Add more skills with proficiency levels',
                'priority': 'medium'
            })
        
        # Keyword suggestions
        if keyword_analysis['missing']:
            top_missing = keyword_analysis['missing'][:5]
            suggestions.append({
                'type': 'keywords',
                'message': f'Consider adding these keywords: {", ".join(top_missing)}',
                'priority': 'medium'
            })
        
        # Action verbs
        suggestions.append({
            'type': 'content',
            'message': 'Use strong action verbs like "achieved", "led", "developed"',
            'priority': 'low'
        })
        
        suggestions.append({
            'type': 'content',
            'message': 'Quantify achievements with numbers and percentages',
            'priority': 'medium'
        })
        
        return suggestions
