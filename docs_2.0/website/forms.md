# Best Practices for Web Forms with Autofill

Designing online web forms that are user-friendly and intuitive can significantly improve user experience and reduce form abandonment. Below are some best practices for creating effective web forms, especially regarding autofill:

## 1. Use Descriptive Labels & Placeholders

- **Clear labels**: Each input field should have a clear, visible label, e.g., "Name" or "Email address."
- **Helpful placeholders**: If using placeholders, make sure they provide guidance (e.g., "Enter your first and last name") and not just repeat the label.

## 2. Enable Native Autocomplete

- **Use `autocomplete` attributes**: HTML supports different autocomplete attributes, such as `"name"`, `"email"`, `"organization"`, etc. This encourages browsers to offer autofill suggestions.
- **Browser-friendly**: Use semantic HTML5 input types (e.g., `type="email"`, `type="password"`, etc.) to allow browsers to optimally handle autofill.

## 3. Keep Forms Short and Focused

- **Ask only for necessary information**: Long or unnecessary forms increase the chance of users abandoning them.
- **Group related fields**: If you have multiple fields, organize them logically (e.g., personal info, payment info) to help with user flow.

## 4. Provide Real-Time Validation

- **Immediate feedback**: Show whether an entry is valid (e.g., if an email is correctly formatted) as users type.
- **Concise error messages**: Provide short, specific error messages that help users correct their mistakes quickly.

## 5. Ensure Accessibility

- **Properly associate labels**: Make sure each label is linked to its corresponding input using the `for` attribute and matching `id`.
- **Keyboard navigation**: All form fields should be reachable and navigable via keyboard (e.g., `Tab`, `Shift+Tab`).
- **Screen reader compatibility**: Include `aria-*` attributes where necessary to ensure forms are easily interpreted by assistive technologies.

## 6. Secure Data Handling

- **Use HTTPS**: Always serve forms over HTTPS to protect user data during transmission.
- **Server-side validation**: Even if you use client-side validation, always validate input on the server side as well.
- **Avoid storing sensitive info**: Never store passwords or sensitive data in plain text logs.

## 7. Make the Submit Button Prominent

- **Highlight the call to action**: Use clear text like "Submit" or "Sign Up."
- **Disable if invalid**: Disable the submit button until the form is valid to prevent accidental submissions.

## 8. Email Integration

### Email Service Architecture

The application uses a centralized email service (`email-service.ts`) to handle all email communications. This ensures consistency and maintainability across different types of emails:

- **Contact Form Emails**
  - User confirmation email with message copy
  - Admin notification with form details
  - Direct reply capability for follow-up

- **Newsletter Subscriptions**
  - Welcome email for new subscribers
  - Unsubscribe functionality
  - Database tracking of subscription status

- **Whitepaper Downloads**
  - Immediate delivery of requested whitepaper
  - Admin notification of downloads
  - Follow-up capability

### Implementation Best Practices

```typescript
// Example usage in components:
await emailService.sendContactForm({
  name: data.name,
  email: data.email,
  message: data.message,
});

await emailService.subscribeToNewsletter({
  email: data.email,
});

await emailService.downloadWhitepaper({
  email: data.email,
  subject: "Ditt whitepaper från Caire: AI inom Hemtjänsten",
  bcc: ["info@caire.se"],
});
```

### Email Template Features

- Responsive design for all email clients
- Branded header with logo and brand bar
- Clear call-to-action buttons
- Reply-to functionality for direct responses
- Unsubscribe links for newsletter emails
- GDPR compliance notices

### Error Handling

- Centralized error handling in the service layer
- Graceful fallbacks for failed email sends
- User-friendly error messages
- Logging for debugging and monitoring
- Retry mechanisms for transient failures

### Database Integration

- Contact form submissions stored in `user_communications` table with type='contact'
- Newsletter subscriptions tracked in `user_consents` table with consent_type='newsletter'
- Whitepaper downloads recorded in `user_communications` table with type='whitepaper'
- User consent tracking in `user_consents` table
- Timestamps for all interactions
- Row-level security policies for data protection

---

# Example: React Component for Contact Form

Below is a React component example that demonstrates how to implement a basic contact form with name and email fields, including best practices such as labels, placeholders, and `autocomplete` attributes.

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email"),
  message: z.string().min(10, "Message must be at least 10 characters"),
  gdprConsent: z.boolean().refine((val) => val === true, {
    message: "You must accept the GDPR terms",
  }),
});

export function ContactForm() {
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      message: "",
      gdprConsent: false,
    },
  });

  const onSubmit = async (data) => {
    try {
      await emailService.sendContactForm(data);
      toast.success("Message sent! We'll get back to you soon.");
    } catch (error) {
      toast.error("Could not send message. Please try again later.");
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <label htmlFor="name">Name</label>
      <input
        id="name"
        type="text"
        {...form.register("name")}
        placeholder="Enter your full name"
        autoComplete="name"
      />
      {form.formState.errors.name && (
        <span>{form.formState.errors.name.message}</span>
      )}

      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        {...form.register("email")}
        placeholder="Enter your email"
        autoComplete="email"
      />
      {form.formState.errors.email && (
        <span>{form.formState.errors.email.message}</span>
      )}

      <label htmlFor="message">Message</label>
      <textarea
        id="message"
        {...form.register("message")}
        placeholder="How can we help you?"
      />
      {form.formState.errors.message && (
        <span>{form.formState.errors.message.message}</span>
      )}

      <label>
        <input
          type="checkbox"
          {...form.register("gdprConsent")}
        />
        I accept the GDPR terms
      </label>
      {form.formState.errors.gdprConsent && (
        <span>{form.formState.errors.gdprConsent.message}</span>
      )}

      <button type="submit" disabled={!form.formState.isValid}>
        Send Message
      </button>
    </form>
  );
}
```
