import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/common'
import { 
  Users, 
  Zap, 
  Mail, 
  BarChart3, 
  Clock, 
  CheckCircle, 
  ArrowRight,
  Star,
  Play,
  ChevronDown,
  Linkedin,
  Twitter,
  Github,
  Menu,
  X
} from 'lucide-react'

export default function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl text-gray-900">Recruiter In A Box</span>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">Features</a>
              <a href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors">Pricing</a>
              <a href="#testimonials" className="text-gray-600 hover:text-gray-900 transition-colors">Testimonials</a>
              <Link to="/login" className="text-gray-600 hover:text-gray-900 transition-colors">Sign In</Link>
              <Link to="/signup">
                <Button>Get Started Free</Button>
              </Link>
            </div>

            <button
              className="md:hidden p-2"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100 px-4 py-4 space-y-4">
            <a href="#features" className="block text-gray-600">Features</a>
            <a href="#pricing" className="block text-gray-600">Pricing</a>
            <a href="#testimonials" className="block text-gray-600">Testimonials</a>
            <Link to="/login" className="block text-gray-600">Sign In</Link>
            <Link to="/signup">
              <Button className="w-full">Get Started Free</Button>
            </Link>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50 -z-10" />
        <div className="absolute top-20 right-0 w-96 h-96 bg-primary-200 rounded-full blur-3xl opacity-20 -z-10" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-secondary-200 rounded-full blur-3xl opacity-20 -z-10" />

        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 rounded-full text-primary-700 text-sm font-medium mb-8">
              <Zap className="w-4 h-4" />
              Powered by AI
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 leading-tight">
              Hire Top Talent
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-secondary-500">
                10x Faster
              </span>
            </h1>

            <p className="mt-6 text-xl text-gray-600 max-w-2xl mx-auto">
              Stop drowning in resumes. Recruiter In A Box uses AI to score candidates, 
              draft outreach emails, and manage your pipeline—so you can focus on finding 
              the right fit.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/signup">
                <Button size="lg" className="w-full sm:w-auto text-lg px-8 py-4">
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Button variant="secondary" size="lg" className="w-full sm:w-auto text-lg px-8 py-4">
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </Button>
            </div>

            <p className="mt-4 text-sm text-gray-500">
              No credit card required • 14-day free trial • Cancel anytime
            </p>

            {/* Social proof */}
            <div className="mt-12 flex flex-col items-center gap-4">
              <div className="flex -space-x-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 border-2 border-white"
                  />
                ))}
              </div>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Star key={i} className="w-5 h-5 fill-warning-400 text-warning-400" />
                ))}
                <span className="ml-2 text-gray-600">Trusted by 2,000+ recruiters</span>
              </div>
            </div>
          </div>

          {/* Hero image/mockup */}
          <div className="mt-16 relative">
            <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 shadow-2xl">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-danger-500" />
                <div className="w-3 h-3 rounded-full bg-warning-500" />
                <div className="w-3 h-3 rounded-full bg-success-500" />
              </div>
              <div className="bg-gray-700 rounded-lg h-80 flex items-center justify-center">
                <div className="text-center text-gray-400">
                  <BarChart3 className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Dashboard Preview</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Hiring shouldn't take weeks
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              The average time-to-hire is 44 days. That's 44 days of screening resumes, 
              sending emails, and chasing candidates. There's a better way.
            </p>
          </div>

          <div className="mt-16 grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-sm">
              <div className="w-12 h-12 bg-danger-100 rounded-xl flex items-center justify-center mb-4">
                <Clock className="w-6 h-6 text-danger-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Time-Consuming</h3>
              <p className="text-gray-600">
                Manually reviewing hundreds of resumes takes hours that could be spent on strategy.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-sm">
              <div className="w-12 h-12 bg-warning-100 rounded-xl flex items-center justify-center mb-4">
                <Mail className="w-6 h-6 text-warning-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Email Overload</h3>
              <p className="text-gray-600">
                Personalized outreach at scale is nearly impossible without burning out.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-sm">
              <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Missed Talent</h3>
              <p className="text-gray-600">
                Great candidates slip through the cracks while you're buried in admin work.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Everything you need to hire smarter
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              From resume parsing to automated outreach, we've got your entire hiring workflow covered.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <FeatureCard
              icon={<Users className="w-6 h-6" />}
              title="AI Candidate Scoring"
              description="Let AI analyze resumes and score candidates based on skills, experience, and education match. Get instant insights on every applicant."
              color="primary"
            />
            <FeatureCard
              icon={<Mail className="w-6 h-6" />}
              title="Smart Email Outreach"
              description="Create templates with variables, send personalized bulk emails, and track engagement—all from one dashboard."
              color="secondary"
            />
            <FeatureCard
              icon={<BarChart3 className="w-6 h-6" />}
              title="Visual Pipeline"
              description="Drag-and-drop Kanban board to manage candidates through every stage of your hiring process."
              color="success"
            />
            <FeatureCard
              icon={<Zap className="w-6 h-6" />}
              title="Resume Parsing"
              description="Upload any PDF resume and watch as AI extracts skills, experience, and contact info automatically."
              color="warning"
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">
              Up and running in minutes
            </h2>
            <p className="mt-4 text-xl text-gray-400">
              Three simple steps to transform your hiring process
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <StepCard
              number={1}
              title="Upload Resumes"
              description="Drag and drop resumes or connect your existing candidate pool. Our AI parses every detail."
            />
            <StepCard
              number={2}
              title="AI Does the Heavy Lifting"
              description="Get instant candidate scores, matched against your job requirements. See who really stands out."
            />
            <StepCard
              number={3}
              title="Engage Top Talent"
              description="Send personalized emails with one click. Track responses and move candidates through your pipeline."
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              Start free, scale as you grow. No hidden fees.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Starter Plan */}
            <div className="bg-white rounded-2xl p-8 border-2 border-gray-200 hover:border-primary-300 transition-colors">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-gray-900">Professional</h3>
                <p className="text-gray-600 mt-1">For individual recruiters</p>
              </div>
              <div className="mb-6">
                <span className="text-5xl font-bold text-gray-900">$99</span>
                <span className="text-gray-600">/month</span>
              </div>
              <ul className="space-y-4 mb-8">
                <PricingFeature text="Up to 100 candidates/month" />
                <PricingFeature text="AI candidate scoring" />
                <PricingFeature text="10 job positions" />
                <PricingFeature text="Email templates & outreach" />
                <PricingFeature text="Basic analytics" />
                <PricingFeature text="Email support" />
              </ul>
              <Link to="/signup" className="block">
                <Button variant="secondary" className="w-full" size="lg">
                  Start Free Trial
                </Button>
              </Link>
            </div>

            {/* Agency Plan */}
            <div className="bg-gradient-to-br from-primary-600 to-secondary-600 rounded-2xl p-8 text-white relative overflow-hidden">
              <div className="absolute top-4 right-4 bg-white/20 px-3 py-1 rounded-full text-sm font-medium">
                Most Popular
              </div>
              <div className="mb-6">
                <h3 className="text-2xl font-bold">Agency</h3>
                <p className="text-white/80 mt-1">For recruiting teams</p>
              </div>
              <div className="mb-6">
                <span className="text-5xl font-bold">$299</span>
                <span className="text-white/80">/month</span>
              </div>
              <ul className="space-y-4 mb-8">
                <PricingFeatureLight text="Unlimited candidates" />
                <PricingFeatureLight text="Everything in Professional" />
                <PricingFeatureLight text="Team collaboration (5 seats)" />
                <PricingFeatureLight text="Advanced analytics & reports" />
                <PricingFeatureLight text="Priority support" />
                <PricingFeatureLight text="Custom branding" />
              </ul>
              <Link to="/signup" className="block">
                <Button variant="secondary" className="w-full bg-white text-primary-600 hover:bg-gray-100" size="lg">
                  Start Free Trial
                </Button>
              </Link>
            </div>
          </div>

          <p className="text-center text-gray-500 mt-8">
            Need enterprise features? <a href="#contact" className="text-primary-600 hover:underline">Contact us</a> for custom pricing.
          </p>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
              Loved by recruiters everywhere
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              See what our customers have to say about their experience
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <TestimonialCard
              quote="Recruiter In A Box cut our time-to-hire by 60%. The AI scoring is incredibly accurate and saves us hours every week."
              author="Sarah Chen"
              role="Head of Talent, TechStart"
              avatar="SC"
            />
            <TestimonialCard
              quote="Finally, a tool that understands what recruiters actually need. The email templates alone are worth the subscription."
              author="Marcus Johnson"
              role="Independent Recruiter"
              avatar="MJ"
            />
            <TestimonialCard
              quote="We've tried every recruitment tool out there. This is the first one that actually uses AI meaningfully."
              author="Emily Rodriguez"
              role="HR Director, GrowthCo"
              avatar="ER"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
            Ready to hire 10x faster?
          </h2>
          <p className="mt-4 text-xl text-gray-600">
            Join 2,000+ recruiters already using AI to find better talent, faster.
          </p>
          <div className="mt-8">
            <Link to="/signup">
              <Button size="lg" className="text-lg px-8 py-4">
                Get Started Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </div>
          <p className="mt-4 text-sm text-gray-500">
            14-day free trial • No credit card required
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold text-xl">Recruiter In A Box</span>
              </div>
              <p className="text-gray-400">
                AI-powered recruitment platform for modern hiring teams.
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Integrations</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#contact" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Cookie Policy</a></li>
              </ul>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-gray-400 text-sm">
              © 2024 Recruiter In A Box. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Scroll indicator */}
      <a href="#features" className="fixed bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <ChevronDown className="w-8 h-8 text-gray-400" />
      </a>
    </div>
  )
}

function FeatureCard({ icon, title, description, color }: { 
  icon: React.ReactNode
  title: string
  description: string
  color: 'primary' | 'secondary' | 'success' | 'warning'
}) {
  const colors = {
    primary: 'bg-primary-100 text-primary-600',
    secondary: 'bg-secondary-100 text-secondary-600',
    success: 'bg-success-100 text-success-600',
    warning: 'bg-warning-100 text-warning-600',
  }

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 hover:shadow-lg transition-shadow">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${colors[color]}`}>
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function StepCard({ number, title, description }: {
  number: number
  title: string
  description: string
}) {
  return (
    <div className="text-center">
      <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl font-bold">{number}</span>
      </div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  )
}

function PricingFeature({ text }: { text: string }) {
  return (
    <li className="flex items-center gap-3">
      <CheckCircle className="w-5 h-5 text-success-500 flex-shrink-0" />
      <span className="text-gray-600">{text}</span>
    </li>
  )
}

function PricingFeatureLight({ text }: { text: string }) {
  return (
    <li className="flex items-center gap-3">
      <CheckCircle className="w-5 h-5 text-white flex-shrink-0" />
      <span className="text-white/90">{text}</span>
    </li>
  )
}

function TestimonialCard({ quote, author, role, avatar }: {
  quote: string
  author: string
  role: string
  avatar: string
}) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="flex items-center gap-1 mb-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <Star key={i} className="w-5 h-5 fill-warning-400 text-warning-400" />
        ))}
      </div>
      <p className="text-gray-600 mb-6">"{quote}"</p>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-medium">
          {avatar}
        </div>
        <div>
          <p className="font-medium text-gray-900">{author}</p>
          <p className="text-sm text-gray-500">{role}</p>
        </div>
      </div>
    </div>
  )
}
