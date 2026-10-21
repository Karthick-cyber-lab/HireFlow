import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser, UserProfile
from jobs.models import JobCategory, Job
from applications.models import Application, Interview, StatusHistory


class Command(BaseCommand):
    help = 'Seeds the database with initial users, jobs, applications, and interviews.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seed...'))

        # 1. Superuser / Admin
        admin_user, created = CustomUser.objects.get_or_create(
            email='admin@hireflow.dev',
            defaults={
                'username': 'admin',
                'first_name': 'Platform',
                'last_name': 'Admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('adminpassword123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin: admin@hireflow.dev / adminpassword123'))
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'bio': 'HireFlow Master Administrator', 'phone': '+91 9876543210', 'location': 'Bengaluru, India'}
        )

        # 2. Recruiters
        recruiter1, created = CustomUser.objects.get_or_create(
            email='sarah@acme.com',
            defaults={
                'username': 'sarah_connor',
                'first_name': 'Sarah',
                'last_name': 'Connor',
                'role': 'recruiter',
            }
        )
        if created:
            recruiter1.set_password('recruiter123')
            recruiter1.save()
        UserProfile.objects.get_or_create(
            user=recruiter1,
            defaults={
                'bio': 'Lead Tech Recruiter at Acme Corp. Hiring passionate software engineers and system architects.',
                'phone': '+91 9876500001',
                'location': 'Bengaluru, India',
                'linkedin_url': 'https://linkedin.com/in/sarah-connor-talent',
            }
        )

        recruiter2, created = CustomUser.objects.get_or_create(
            email='david@cloudscale.io',
            defaults={
                'username': 'david_miller',
                'first_name': 'David',
                'last_name': 'Miller',
                'role': 'recruiter',
            }
        )
        if created:
            recruiter2.set_password('recruiter123')
            recruiter2.save()
        UserProfile.objects.get_or_create(
            user=recruiter2,
            defaults={
                'bio': 'Talent Partner at CloudScale Technologies. Scaling cloud infrastructure and SRE teams.',
                'phone': '+91 9876500002',
                'location': 'Pune, India',
                'linkedin_url': 'https://linkedin.com/in/david-miller-cloud',
            }
        )

        # 3. Applicants
        john, created = CustomUser.objects.get_or_create(
            email='john@hireflow.dev',
            defaults={
                'username': 'john_doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'applicant',
            }
        )
        if created:
            john.set_password('applicant123')
            john.save()
        UserProfile.objects.get_or_create(
            user=john,
            defaults={
                'bio': 'Senior Full-Stack Python & Django Developer with 5+ years building scalable distributed microservices, REST APIs, and modern web applications.',
                'phone': '+91 9123456780',
                'location': 'Bengaluru, India',
                'linkedin_url': 'https://linkedin.com/in/john-doe-dev',
                'github_url': 'https://github.com/johndoe',
                'portfolio_url': 'https://johndoe.dev',
                'skills': 'Python, Django, PostgreSQL, Docker, Redis, Celery, React, AWS',
                'experience_years': 5,
            }
        )

        jane, created = CustomUser.objects.get_or_create(
            email='jane@hireflow.dev',
            defaults={
                'username': 'jane_smith',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'applicant',
            }
        )
        if created:
            jane.set_password('applicant123')
            jane.save()
        UserProfile.objects.get_or_create(
            user=jane,
            defaults={
                'bio': 'Frontend UI/UX Engineer passionate about building accessible, responsive, high-performance web interfaces with React, TypeScript, and modern CSS.',
                'phone': '+91 9123456781',
                'location': 'Hyderabad, India',
                'linkedin_url': 'https://linkedin.com/in/jane-smith-ui',
                'github_url': 'https://github.com/janesmith',
                'skills': 'React, TypeScript, Next.js, Tailwind CSS, JavaScript, HTML5/CSS3, Figma',
                'experience_years': 3,
            }
        )

        alex, created = CustomUser.objects.get_or_create(
            email='alex@hireflow.dev',
            defaults={
                'username': 'alex_chen',
                'first_name': 'Alex',
                'last_name': 'Chen',
                'role': 'applicant',
            }
        )
        if created:
            alex.set_password('applicant123')
            alex.save()
        UserProfile.objects.get_or_create(
            user=alex,
            defaults={
                'bio': 'DevOps & Site Reliability Engineer experienced in Kubernetes, Terraform, AWS multi-region infrastructure, and automated CI/CD pipelines.',
                'phone': '+91 9123456782',
                'location': 'Pune, India',
                'linkedin_url': 'https://linkedin.com/in/alex-chen-devops',
                'github_url': 'https://github.com/alexchen',
                'skills': 'Kubernetes, Docker, Terraform, AWS, Linux, GitHub Actions, Prometheus, Python',
                'experience_years': 4,
            }
        )

        # 4. Categories
        categories_data = [
            {'name': 'Software Engineering', 'slug': 'software-engineering', 'icon': 'code-slash', 'description': 'Full-stack, backend, and core software development roles.'},
            {'name': 'Cloud & DevOps', 'slug': 'cloud-devops', 'icon': 'cloud', 'description': 'Infrastructure, SRE, CI/CD, and cloud platforms.'},
            {'name': 'Frontend & UI/UX', 'slug': 'frontend-ui-ux', 'icon': 'palette', 'description': 'User interfaces, product design, and frontend engineering.'},
            {'name': 'Data & AI', 'slug': 'data-ai', 'icon': 'graph-up', 'description': 'Machine learning, data science, and analytical engineering.'},
            {'name': 'Product & Agile', 'slug': 'product-agile', 'icon': 'kanban', 'description': 'Product management, agile coaching, and scrum masters.'},
        ]
        cats = {}
        for cdata in categories_data:
            cat, _ = JobCategory.objects.get_or_create(slug=cdata['slug'], defaults=cdata)
            cats[cdata['slug']] = cat

        # 5. Jobs
        today = timezone.now().date()
        deadline_30d = today + datetime.timedelta(days=30)
        deadline_45d = today + datetime.timedelta(days=45)

        jobs_data = [
            {
                'recruiter': recruiter1,
                'category': cats['software-engineering'],
                'title': 'Senior Python & Django Architect',
                'company': 'Acme Corp',
                'location': 'Bengaluru, India (Remote Available)',
                'job_type': 'remote',
                'experience_level': 'senior',
                'salary_min': 180000,
                'salary_max': 250000,
                'skills_required': 'Python, Django, PostgreSQL, Redis, Docker, Celery, REST API',
                'vacancies': 2,
                'deadline': deadline_30d,
                'status': 'active',
                'is_featured': True,
                'description': 'We are looking for an experienced Senior Python/Django Architect to spearhead our next-generation enterprise SaaS platform. You will design reliable microservices, architect scalable data layers, and mentor our growing engineering team.',
                'requirements': '• 5+ years of production experience in Python and Django.\n• Strong grasp of database optimization (PostgreSQL, indexes, query plans).\n• Experience with async queues (Celery, RabbitMQ/Redis).\n• Proven track record designing RESTful APIs and distributed architectures.\n• Solid understanding of containerization (Docker, Kubernetes).',
                'responsibilities': '• Lead the backend architecture and tech stack decisions.\n• Write high-quality, well-tested Python code.\n• Review pull requests and foster engineering excellence.\n• Collaborate with product managers and frontend teams to ship high-impact features.',
            },
            {
                'recruiter': recruiter1,
                'category': cats['frontend-ui-ux'],
                'title': 'Senior Frontend React Engineer',
                'company': 'Acme Corp',
                'location': 'Bengaluru, India',
                'job_type': 'hybrid',
                'experience_level': 'senior',
                'salary_min': 150000,
                'salary_max': 210000,
                'skills_required': 'React, TypeScript, Next.js, Redux, CSS3, Responsive Design',
                'vacancies': 3,
                'deadline': deadline_30d,
                'status': 'active',
                'is_featured': True,
                'description': 'Acme Corp is seeking a talented Frontend Engineer to craft sleek, responsive, and intuitive web user experiences across our SaaS product lines.',
                'requirements': '• 3+ years experience with React and TypeScript.\n• Deep familiarity with modern CSS (Flexbox, Grid, CSS modules/Tailwind).\n• Strong understanding of web performance, Core Web Vitals, and accessibility (WCAG).\n• Experience integrating RESTful APIs and WebSocket feeds.',
                'responsibilities': '• Build beautiful, reactive user interfaces.\n• Maintain and expand our design system components.\n• Optimize bundle sizes and render performance.',
            },
            {
                'recruiter': recruiter2,
                'category': cats['cloud-devops'],
                'title': 'Lead DevOps & Cloud Engineer',
                'company': 'CloudScale Technologies',
                'location': 'Pune, India',
                'job_type': 'full_time',
                'experience_level': 'lead',
                'salary_min': 200000,
                'salary_max': 280000,
                'skills_required': 'Kubernetes, AWS, Terraform, Docker, CI/CD, Prometheus, Linux',
                'vacancies': 1,
                'deadline': deadline_45d,
                'status': 'active',
                'is_featured': True,
                'description': 'Join CloudScale Technologies as our Lead DevOps Engineer to oversee cloud infrastructure, automate deployment pipelines, and ensure 99.99% system availability.',
                'requirements': '• 5+ years in DevOps / SRE roles with AWS infrastructure.\n• Production expertise with Kubernetes (EKS/k8s) and Terraform IaC.\n• Experience setting up zero-downtime CI/CD pipelines.\n• Knowledge of monitoring tools: Prometheus, Grafana, ELK stack.',
                'responsibilities': '• Architect and maintain resilient multi-region AWS environments.\n• Enforce security best practices, secrets management, and compliance.\n• Automate deployment, scaling, and recovery workflows.',
            },
            {
                'recruiter': recruiter2,
                'category': cats['data-ai'],
                'title': 'Machine Learning / AI Engineer',
                'company': 'CloudScale Technologies',
                'location': 'Remote',
                'job_type': 'remote',
                'experience_level': 'mid',
                'salary_min': 160000,
                'salary_max': 240000,
                'skills_required': 'Python, PyTorch, Scikit-Learn, LLMs, FastAPI, MLOps, SQL',
                'vacancies': 2,
                'deadline': deadline_30d,
                'status': 'active',
                'is_featured': False,
                'description': 'We are looking for an ML/AI Engineer to develop intelligent recommendation engines, NLP workflows, and LLM-powered applications.',
                'requirements': '• 2-4 years experience in machine learning and data pipelines.\n• Proficiency in Python and modern ML frameworks (PyTorch, HuggingFace).\n• Experience deploying models with FastAPI or Triton.\n• Familiarity with Vector databases and Retrieval-Augmented Generation (RAG).',
                'responsibilities': '• Train, fine-tune, and evaluate ML and LLM models.\n• Build low-latency inference APIs.\n• Collaborate with product teams on AI-assisted feature development.',
            },
            {
                'recruiter': recruiter1,
                'category': cats['product-agile'],
                'title': 'Technical Product Manager',
                'company': 'Acme Corp',
                'location': 'Bengaluru, India',
                'job_type': 'hybrid',
                'experience_level': 'mid',
                'salary_min': 170000,
                'salary_max': 230000,
                'skills_required': 'Product Management, Agile, User Stories, Roadmapping, SQL, JIRA',
                'vacancies': 1,
                'deadline': deadline_30d,
                'status': 'active',
                'is_featured': False,
                'description': 'Help drive product strategy and execution for our developer platform and enterprise tooling products.',
                'requirements': '• 3+ years experience as a technical PM or technical lead.\n• Experience conducting user research and synthesizing product specs.\n• Data-informed mindset with SQL querying skills.',
                'responsibilities': '• Define product roadmaps and sprint backlogs.\n• Coordinate with engineering, design, and business stakeholders.\n• Track KPIs and analyze feature adoption.',
            },
        ]

        created_jobs = []
        for jdata in jobs_data:
            job, _ = Job.objects.get_or_create(
                title=jdata['title'],
                company=jdata['company'],
                defaults=jdata,
            )
            created_jobs.append(job)

        self.stdout.write(self.style.SUCCESS(f'Created/verified {len(created_jobs)} jobs.'))

        # 6. Applications across stages
        job_python = created_jobs[0]
        job_react = created_jobs[1]
        job_devops = created_jobs[2]

        # App 1: John Doe -> Python Architect (Interview Scheduled)
        app1, _ = Application.objects.get_or_create(
            job=job_python,
            applicant=john,
            defaults={
                'status': 'interview',
                'cover_letter': 'Dear Hiring Manager,\n\nI am thrilled to apply for the Senior Python & Django Architect role at Acme Corp. With over 5 years of hands-on experience building high-throughput Python backends and optimizing database architectures, I am confident in my ability to immediately contribute to your team.\n\nLooking forward to speaking with you.\n\nBest regards,\nJohn Doe',
                'recruiter_notes': 'Exceptional profile. Strong Django and PostgreSQL background. Scheduled for Technical Round with Lead Architect.',
            }
        )
        StatusHistory.objects.get_or_create(
            application=app1,
            from_status='applied',
            to_status='shortlisted',
            changed_by=recruiter1,
            defaults={'note': 'Resume shortlisted based on relevant Django & AWS expertise.'}
        )
        StatusHistory.objects.get_or_create(
            application=app1,
            from_status='shortlisted',
            to_status='interview',
            changed_by=recruiter1,
            defaults={'note': 'Technical interview scheduled.'}
        )
        interview_time = timezone.now() + datetime.timedelta(days=2, hours=3)
        Interview.objects.get_or_create(
            application=app1,
            scheduled_at=interview_time,
            defaults={
                'duration_minutes': 60,
                'mode': 'online',
                'interviewer_name': 'Sarah Connor & Lead Architect',
                'meeting_link': 'https://meet.google.com/hfw-arch-tech',
                'notes': 'Focus on system design, database indexing, and async task orchestration.',
                'result': 'pending',
            }
        )

        # App 2: Jane Smith -> Frontend React (Shortlisted)
        app2, _ = Application.objects.get_or_create(
            job=job_react,
            applicant=jane,
            defaults={
                'status': 'shortlisted',
                'cover_letter': 'Hi Sarah,\n\nI love building performant, pixel-perfect user interfaces with React and TypeScript. I have spent the last 3 years crafting responsive enterprise design systems and would love to bring my skills to Acme Corp.\n\nWarm regards,\nJane Smith',
                'recruiter_notes': 'Portfolio links look stunning. Clean code in GitHub repositories. Recommended for initial phone screen.',
            }
        )
        StatusHistory.objects.get_or_create(
            application=app2,
            from_status='applied',
            to_status='shortlisted',
            changed_by=recruiter1,
            defaults={'note': 'Shortlisted due to high-quality portfolio and strong React background.'}
        )

        # App 3: Alex Chen -> DevOps (Selected)
        app3, _ = Application.objects.get_or_create(
            job=job_devops,
            applicant=alex,
            defaults={
                'status': 'selected',
                'cover_letter': 'Hello David,\n\nI have extensive experience architecting Kubernetes clusters and automating Terraform configurations for AWS enterprise environments. I would be thrilled to join CloudScale Technologies as Lead DevOps Engineer.\n\nSincerely,\nAlex Chen',
                'recruiter_notes': 'Aced both the technical and culture rounds. Outstanding Terraform live coding. Offer extended and candidate accepted!',
            }
        )
        StatusHistory.objects.get_or_create(
            application=app3,
            from_status='applied',
            to_status='shortlisted',
            changed_by=recruiter2,
            defaults={'note': 'Strong candidate profile.'}
        )
        StatusHistory.objects.get_or_create(
            application=app3,
            from_status='shortlisted',
            to_status='interview',
            changed_by=recruiter2,
            defaults={'note': 'System design interview scheduled.'}
        )
        StatusHistory.objects.get_or_create(
            application=app3,
            from_status='interview',
            to_status='selected',
            changed_by=recruiter2,
            defaults={'note': 'Candidate selected! Offer accepted.'}
        )
        past_interview_time = timezone.now() - datetime.timedelta(days=3)
        Interview.objects.get_or_create(
            application=app3,
            scheduled_at=past_interview_time,
            defaults={
                'duration_minutes': 75,
                'mode': 'online',
                'interviewer_name': 'David Miller & VP of Engineering',
                'meeting_link': 'https://meet.google.com/cst-devops-round',
                'notes': 'Deep dive into Kubernetes security, disaster recovery, and cost optimization.',
                'result': 'passed',
                'feedback': 'Excellent domain knowledge, clear communicator, strong cultural fit.',
            }
        )

        # App 4: John Doe -> DevOps (Rejected - skillset mismatch)
        app4, _ = Application.objects.get_or_create(
            job=job_devops,
            applicant=john,
            defaults={
                'status': 'rejected',
                'cover_letter': 'Applying for the Lead DevOps role to expand into full cloud infrastructure management.',
                'recruiter_notes': 'Great backend developer but looking for deeper specialized K8s/IaC experience for this lead role.',
            }
        )
        StatusHistory.objects.get_or_create(
            application=app4,
            from_status='applied',
            to_status='rejected',
            changed_by=recruiter2,
            defaults={'note': 'Position requires 5+ years dedicated SRE/K8s experience.'}
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded sample applications, interviews, and pipeline history!'))
        self.stdout.write(self.style.SUCCESS('\n=== DEMO CREDENTIALS ==='))
        self.stdout.write(self.style.SUCCESS('Admin:       admin@hireflow.dev       / adminpassword123'))
        self.stdout.write(self.style.SUCCESS('Recruiter 1: sarah@acme.com           / recruiter123'))
        self.stdout.write(self.style.SUCCESS('Recruiter 2: david@cloudscale.io      / recruiter123'))
        self.stdout.write(self.style.SUCCESS('Applicant 1: john@hireflow.dev        / applicant123'))
        self.stdout.write(self.style.SUCCESS('Applicant 2: jane@hireflow.dev        / applicant123'))
        self.stdout.write(self.style.SUCCESS('Applicant 3: alex@hireflow.dev        / applicant123'))
        self.stdout.write(self.style.SUCCESS('=========================\n'))
