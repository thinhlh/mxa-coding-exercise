import { useEffect, useId, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import styles from './Modal.module.css'

interface ModalProps {
  title: string
  onClose: () => void
  children: ReactNode
}

// The design system draws the modal (.dialog-backdrop / .dialog / .dialog-title); this
// component supplies the behaviour it can't: a portal so nothing clips it, Escape and
// backdrop-click to dismiss, and focus that enters on open and goes back where it came
// from on close.
export function Modal({ title, onClose, children }: ModalProps) {
  const titleId = useId()
  const dialogRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null
    dialogRef.current?.querySelector<HTMLElement>('input, textarea, select, button')?.focus()

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      previouslyFocused?.focus()
    }
  }, [onClose])

  return createPortal(
    <div
      className={`dialog-backdrop ${styles.backdrop}`}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div className="dialog" role="dialog" aria-modal="true" aria-labelledby={titleId} ref={dialogRef}>
        <div className="dialog-title" id={titleId}>
          {title}
        </div>
        {children}
      </div>
    </div>,
    document.body,
  )
}
