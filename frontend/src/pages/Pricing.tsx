import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { subscriptionsApi } from '@/services/api'
import { Button } from '@/components/common'
import { CheckCircle, X, Crown, Zap, ArrowRight } from 'lucide-react'
import { cn } from '@/utils'

interface PlanLimits {
  candidates_per_month: number
  job_positions: number
  team_seats: number
  ai_scoring: boolean
  email_outreach: boolean
  analytics: string
  support: string
  custom_branding?: boolean
}

interface SubscriptionStatus {
  plan_limits: PlanLimits
  trial_days_remaining?: number
  trial_expired: boolean
  subscription?: {
    plan_type: string
    status: string
    cancel_at_period_end: boolean
  }
}

const plans = [
  {
    id: 'professional',
    name: 'Professional',
    price: 99,
    description: 'Perfect for individual recruiters',
    features: [
      { text: 'Up to 100 candidates/month', included: true },
      { text: 'AI candidate scoring', included: true },
      { text: '10 job positions', included: true },
      { text: 'Email templates & outreach', included: true },
      { text: 'Basic analytics', included: true },
      { text: 'Email support', included: true },
      { text: 'Team collaboration', included: false },
      { text: 'Advanced analytics', included: false },
      { text: 'Custom branding', included: false },
    ],
  },
  {
    id: 'agency',
    name: 'Agency',
    price: 299,
    description: 'For recruiting teams',
    popular: true,
    features: [
      { text: 'Unlimited candidates', included: true },
      { text: 'AI candidate scoring', included: true },
      { text: 'Unlimited job positions', included: true },
      { text: 'Email templates & outreach', included: true },
      { text: 'Advanced analytics & reports', included: true },
      { text: 'Priority support', included: true },
      { text: 'Team collaboration (5 seats)', included: true },
      { text: 'Custom branding', included: true },
    ],
  },
]

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly')

  const { data: subscriptionStatus } = useQuery({
    queryKey: ['subscription-status'],
    queryFn: () => subscriptionsApi.getStatus(),
  })

  const checkoutMutation = useMutation({
    mutationFn: (plan: string) => subscriptionsApi.createCheckout(plan),
    onSuccess: (data) => {
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      }
    },
  })

  const status = subscriptionStatus as SubscriptionStatus | undefined
  const currentPlan = status?.subscription?.plan_type || 'trial'

  const getAnnualPrice = (monthly: number) => Math.floor(monthly * 0.8)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 text-center">
            Simple, Transparent Pricing
          </h1>
          <p className="text-gray-600 text-center mt-2">
            Start with a 14-day free trial. No credit card required.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mt-6">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={cn(
                'px-4 py-2 rounded-lg font-medium transition-colors',
                billingCycle === 'monthly'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={cn(
                'px-4 py-2 rounded-lg font-medium transition-colors',
                billingCycle === 'annual'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              Annual
              <span className="ml-2 text-xs bg-success-100 text-success-700 px-2 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </div>

          {/* Trial Banner */}
          {status?.trial_days_remaining !== undefined && status.trial_days_remaining > 0 && (
            <div className="mt-6 max-w-md mx-auto">
              <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 text-center">
                <p className="text-primary-700">
                  <strong>{status.trial_days_remaining} days</strong> remaining in your free trial
                </p>
                <p className="text-sm text-primary-600 mt-1">
                  Upgrade now to unlock all features
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {plans.map((plan) => {
            const isCurrentPlan = currentPlan === plan.id
            const price = billingCycle === 'annual' ? getAnnualPrice(plan.price) : plan.price

            return (
              <div
                key={plan.id}
                className={cn(
                  'relative bg-white rounded-2xl shadow-lg overflow-hidden',
                  plan.popular && 'ring-2 ring-primary-500'
                )}
              >
                {plan.popular && (
                  <div className="absolute top-0 right-0 bg-primary-500 text-white px-4 py-1 text-sm font-medium rounded-bl-lg">
                    Most Popular
                  </div>
                )}

                <div className="p-8">
                  <div className="flex items-center gap-3 mb-4">
                    {plan.id === 'agency' ? (
                      <Crown className="w-8 h-8 text-primary-500" />
                    ) : (
                      <Zap className="w-8 h-8 text-primary-500" />
                    )}
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                      <p className="text-sm text-gray-500">{plan.description}</p>
                    </div>
                  </div>

                  <div className="mb-6">
                    <span className="text-4xl font-bold text-gray-900">${price}</span>
                    <span className="text-gray-500">/month</span>
                    {billingCycle === 'annual' && (
                      <p className="text-sm text-success-600 mt-1">
                        ${price * 12} billed annually
                      </p>
                    )}
                  </div>

                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-3">
                        {feature.included ? (
                          <CheckCircle className="w-5 h-5 text-success-500 flex-shrink-0" />
                        ) : (
                          <X className="w-5 h-5 text-gray-300 flex-shrink-0" />
                        )}
                        <span className={cn(
                          feature.included ? 'text-gray-700' : 'text-gray-400'
                        )}>
                          {feature.text}
                        </span>
                      </li>
                    ))}
                  </ul>

                  {isCurrentPlan ? (
                    <Button variant="secondary" className="w-full" disabled>
                      Current Plan
                    </Button>
                  ) : (
                    <Button
                      className="w-full"
                      variant={plan.popular ? 'primary' : 'secondary'}
                      onClick={() => checkoutMutation.mutate(plan.id)}
                      isLoading={checkoutMutation.isPending}
                    >
                      {status?.trial_expired || currentPlan !== 'trial' ? 'Upgrade' : 'Start Free Trial'}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* FAQ Section */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Frequently Asked Questions
          </h2>
          <div className="space-y-4">
            <FaqItem
              question="Can I change plans at any time?"
              answer="Yes, you can upgrade or downgrade your plan at any time. If you upgrade, you'll be charged the prorated difference. If you downgrade, the change will take effect at the end of your billing period."
            />
            <FaqItem
              question="What happens after my 14-day trial?"
              answer="After your trial ends, you'll need to upgrade to a paid plan to continue using the service. Your data will be preserved for 30 days after the trial ends."
            />
            <FaqItem
              question="Can I cancel my subscription?"
              answer="Yes, you can cancel at any time. If you cancel, you'll continue to have access until the end of your current billing period."
            />
            <FaqItem
              question="Do you offer refunds?"
              answer="We offer a 30-day money-back guarantee for all new subscriptions. If you're not satisfied, contact us within 30 days for a full refund."
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function FaqItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 text-left flex items-center justify-between"
      >
        <span className="font-medium text-gray-900">{question}</span>
        <ChevronDownIcon className={cn(
          'w-5 h-5 text-gray-500 transition-transform',
          isOpen && 'rotate-180'
        )} />
      </button>
      {isOpen && (
        <div className="px-6 pb-4">
          <p className="text-gray-600">{answer}</p>
        </div>
      )}
    </div>
  )
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  )
}
