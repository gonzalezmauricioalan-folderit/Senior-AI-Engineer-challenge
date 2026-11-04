interface Props {
  message: string;
  /** When given, an error-style message with a Retry button. */
  onRetry?: () => void;
}

export default function StateMessage({ message, onRetry }: Props) {
  if (onRetry) {
    return (
      <div className="state-message" role="alert">
        <p>{message}</p>
        <button type="button" onClick={onRetry}>
          Retry
        </button>
      </div>
    );
  }
  return (
    <p className="state-message muted" role="status">
      {message}
    </p>
  );
}
