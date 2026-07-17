import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { onboardingApi } from '@/services/api'
import { Button } from '@/components/common'
import { Modal } from '@/components/common/Modal'
import { CheckCircle, ArrowRight, ArrowLeft, Zap, Briefcase, Users, Mail, Settings } from 'lucide-react'
import { cn } from '@/utils'

interface OnboardingProgress {
  step_profile_completed: boolean
  step_first_job_completed: boolean
  step_first_candidate_completed: boolean
  step_first_email_completed: boolean
  step_integration_completed: boolean
  current_step: number
  total_steps: number
  tour_completed: boolean
  progress_percentage: number
}

const STEPS = [
  {
    id: 'profile',
    name: 'Complete Profile',
    description: 'Add your company information',
    icon: Settings,
  },
  {
    id: 'first_job',
    name: 'Create First Job',
    description: 'Add a job position to recruit for',
    icon: Briefcase,
  },
  {
    id: 'first_candidate',
    name: 'Add Candidate',
    description: 'Upload resumes or add candidates manually',
    icon: Users,
  },
  {
    id: 'first_email',
    name: 'Create Email Template',
    description: 'Set up your outreach templates',
    icon: Mail,
  },
  {
    id: 'integration',
    name: 'Connect Integrations',
    description: 'Link your calendar and email',
    icon: Zap,
  },
]

export default function OnboardingModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const queryClient = useQueryClient()

  const { data: progress } = useQuery({
    queryKey: ['onboarding-progress'],
    queryFn: () => onboardingApi.getProgress(),
  })

  const dismissMutation = useMutation({
    mutationFn: () => onboardingApi.dismissTour(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['onboarding-progress'] })
      setIsOpen(false)
    },
  })

  // Show onboarding modal if user hasn't completed tour and has low progress
  useEffect(() => {
    const progressData = progress as OnboardingProgress | undefined
    if (progressData && !progressData.tour_completed && progressData.progress_percentage < 100) {
      setIsOpen(true)
    }
  }, [progress])

  if (!progress) return null

  const progressData = progress as OnboardingProgress
  const completedSteps = [
    progressData.step_profile_completed,
    progressData.step_first_job_completed,
    progressData.step_first_candidate_completed,
    progressData.step_first_email_completed,
    progressData.step_integration_completed,
  ]

  const isStepCompleted = (index: number) => completedSteps[index]

  return (
    <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="lg">
      <div className="p-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Welcome to Recruiter In A Box!</h2>
          <p className="text-gray-600 mt-2">
            Let's get you set up in a few quick steps
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{progressData.progress_percentage}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full">
            <div
              className="h-full bg-primary-500 rounded-full transition-all"
              style={{ width: `${progressData.progress_percentage}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3 mb-8">
          {STEPS.map((step, index) => {
            const Icon = step.icon
            const completed = isStepCompleted(index)
            const isCurrent = index === currentStep

            return (
              <div
                key={step.id}
                className={cn(
                  'flex items-center gap-4 p-4 rounded-lg border-2 transition-all cursor-pointer',
                  isCurrent
                    ? 'border-primary-500 bg-primary-50'
                    : completed
                    ? 'border-success-200 bg-success-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
                onClick={() => setCurrentStep(index)}
              >
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center',
                    completed
                      ? 'bg-success-100 text-success-600'
                      : isCurrent
                      ? 'bg-primary-100 text-primary-600'
                      : 'bg-gray-100 text-gray-400'
                  )}
                >
                  {completed ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <div className="flex-1">
                  <p className={cn(
                    'font-medium',
                    completed ? 'text-success-700' : isCurrent ? 'text-primary-700' : 'text-gray-700'
                  )}>
                    {step.name}
                  </p>
                  <p className="text-sm text-gray-500">{step.description}</p>
                </div>
                {completed && (
                  <span className="text-xs text-success-600 font-medium">Completed</span>
                )}
              </div>
            )
          })}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              Step {currentStep + 1} of {STEPS.length}
            </span>
            <Button
              size="sm"
              onClick={() => setCurrentStep(Math.min(STEPS.length - 1, currentStep + 1))}
              disabled={currentStep === STEPS.length - 1}
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>

        {/* Skip */}
        <div className="text-center mt-4">
          <button
            onClick={() => dismissMutation.mutate()}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Skip setup for now
          </button>
        </div>
      </div>
    </Modal>
  )
}
