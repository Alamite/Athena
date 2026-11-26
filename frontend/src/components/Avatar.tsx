import logo from '../assets/athena-logo-mark.png'

/** Athena's avatar next to assistant messages. */
export function Avatar() {
  return (
    <div className="avatar">
      <img src={logo} alt="" />
    </div>
  )
}
