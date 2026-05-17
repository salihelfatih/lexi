import { Button } from "./ui/button";
import { Dialog } from "./ui/dialog";

export function LexiBoundariesModal({ open, onAcknowledge }) {
  return (
    <Dialog
      open={open}
      title="Before you begin"
      description="A quick trust and boundaries reminder."
      onClose={onAcknowledge}
      footer={
        <Button onClick={onAcknowledge}>
          I understand
        </Button>
      }
    >
      <ul className="dialog-list">
        <li>Lexi explains legal text in plain language.</li>
        <li>Lexi can suggest questions worth asking.</li>
        <li>Lexi does not replace a lawyer or legal clinic.</li>
        <li>If stakes are high, verify with qualified legal support.</li>
      </ul>
    </Dialog>
  );
}
