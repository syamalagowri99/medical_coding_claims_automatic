import { cn } from '../utils/cn'

export default function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
        className
      )}
      {...props}
    />
  )
}
