import { cn } from '../utils/cn'

export default function Button({ children, variant = 'primary', className, ...props }) {
  const baseStyles = 'px-4 py-2 rounded-md font-medium transition-colors duration-200'
  
  const variants = {
    primary: 'bg-primary-500 text-white hover:bg-primary-600',
    secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
    danger: 'bg-red-500 text-white hover:bg-red-600',
    ghost: 'text-gray-700 hover:bg-gray-100',
  }

  return (
    <button
      className={cn(baseStyles, variants[variant], className)}
      {...props}
    >
      {children}
    </button>
  )
}
