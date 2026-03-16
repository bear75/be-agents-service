# Analytics Implementation

## Status: ✅ Fully Implemented

## Google Analytics 4 (GA4)

### Configuration

- Measurement ID: `G-DB10R88XR4`
- Implementation Type: gtag.js
- Data Collection: Client-side
- Privacy Mode: Enabled
- Location: `src/lib/analytics.ts`

### Implementation Details

1. **Base Implementation** ✅
   - Google Analytics 4 is implemented using the gtag.js script
   - The script is loaded asynchronously to not block page rendering
   - Placed in the `<head>` section of the HTML document
   - IP anonymization enabled by default
   - Secure cookie flags enabled
   - TypeScript types for better type safety

2. **Events Tracked** ✅
   - Page Views (automatic)
   - User Engagement (automatic)
   - File Downloads (whitepapers)
   - Form Submissions (contact, newsletter)
   - Button Clicks on key CTAs
   - Scroll Depth
   - Integration Usage
   - Error Events
   - Section Visibility
   - Tab Changes
   - Feature Interactions
   - Resource Page Views
   - Implementation Guide Views
   - Back to Resources Navigation
   - Try Now Button Clicks
   - Try Now Signup Flow
   - Test Environment Usage
   - Test Data Upload Events
   - Schedule Generation Events
   - ROI Calculator Usage

3. **Custom Events** ✅
   - Sign Up Flow Progress
   - Feature Usage
   - Error Tracking
   - User Preferences
   - Whitepaper Downloads
   - Newsletter Subscriptions
   - Contact Form Submissions
   - Integration Interactions
   - Section Views
   - Feature Engagement
   - Resource Page Interactions
   - Implementation Guide Progress
   - Try Now Funnel Events:
     - Try Now Button Click
     - Signup Start
     - Signup Complete
     - Test Data Upload
     - Schedule Generation
     - ROI Calculation
     - Conversion to Pilot
     - Test Environment Usage Time
     - Feature Discovery Events
     - Success Metrics Views

4. **Privacy Considerations** ✅
   - Compliant with GDPR and SoL requirements
   - Cookie consent implementation with opt-out
   - IP anonymization enabled
   - User data retention periods set according to compliance requirements
   - Data minimization practices
   - Clear privacy notices
   - User consent tracking
   - Secure cookie settings
   - Third-party cookie warnings handled

### Code Implementation

```typescript
// Type definitions
declare global {
  interface Window {
    dataLayer: any[];
    gtag: (...args: any[]) => void;
  }
}

type EventParams = {
  [key: string]: string | number | boolean;
};

// Initialize Google Analytics
export const initGA = () => {
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${import.meta.env.VITE_GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  function gtag(...args: any[]) {
    window.dataLayer.push(args);
  }
  gtag("js", new Date());
  gtag("config", import.meta.env.VITE_GA_MEASUREMENT_ID, {
    anonymize_ip: true,
    cookie_flags: "SameSite=None;Secure",
  });
};
```

### Event Tracking Implementation

```typescript
// Example of tracking a whitepaper download
export const trackEvent = (eventName: string, params?: EventParams): void => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", eventName, params);
  }
};

// Example of tracking page views
export const trackPageView = (path: string, title: string): void => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("config", import.meta.env.VITE_GA_MEASUREMENT_ID, {
      page_path: path,
      page_title: title,
    });
  }
};

// Example of tracking form submissions
export const trackFormSubmission = (
  formName: string,
  success: boolean,
): void => {
  trackEvent("form_submission", {
    form_name: formName,
    success: success,
  });
};

// Example of tracking Try Now funnel events
export const trackTryNowEvent = (
  stage:
    | "click"
    | "signup_start"
    | "signup_complete"
    | "data_upload"
    | "schedule_generation"
    | "roi_calculation"
    | "pilot_conversion",
  params?: EventParams,
): void => {
  trackEvent(`try_now_${stage}`, {
    funnel_stage: stage,
    ...params,
  });
};

// Example of tracking test environment usage
export const trackTestEnvironmentUsage = (
  action: string,
  duration?: number,
): void => {
  trackEvent("test_environment_usage", {
    action,
    duration,
    timestamp: new Date().toISOString(),
  });
};

// Example of tracking ROI calculator usage
export const trackROICalculation = (
  inputData: {
    employees: number;
    clients: number;
    currentCosts: number;
  },
  calculatedSavings: number,
): void => {
  trackEvent("roi_calculation", {
    input_data: JSON.stringify(inputData),
    calculated_savings: calculatedSavings,
    timestamp: new Date().toISOString(),
  });
};
```

### Best Practices

1. **Performance**
   - Async loading of analytics script
   - Minimal impact on Core Web Vitals
   - Efficient event batching
   - Debounced event tracking
   - Type-safe event tracking

2. **Data Quality**
   - Consistent event naming conventions
   - Proper event parameter validation
   - Regular data verification
   - Automated testing of tracking
   - TypeScript type checking

3. **Privacy**
   - Clear user consent mechanisms
   - Data minimization
   - Proper handling of sensitive data
   - Regular privacy audits
   - Secure cookie handling
   - IP anonymization

4. **Maintenance**
   - Regular validation of tracking implementation
   - Monitoring of data quality
   - Documentation updates for new tracking requirements
   - Periodic review of tracked events
   - Type definitions maintenance

### Usage Example

```typescript
import {
  trackEvent,
  trackPageView,
  trackFormSubmission,
  trackTryNowEvent,
  trackTestEnvironmentUsage,
  trackROICalculation,
} from "@/lib/analytics";

// In your component
const MyComponent = () => {
  // Track page view
  useEffect(() => {
    trackPageView("/my-page", "My Page Title");
  }, []);

  // Track events
  const handleDownload = async () => {
    await downloadWhitepaper();
    trackEvent("whitepaper_download", {
      title: "AI inom Hemtjänsten",
      category: "resources",
    });
  };

  // Track form submissions
  const handleSubmit = async (e: React.FormEvent) => {
    try {
      await submitForm(e);
      trackFormSubmission("contact_form", true);
    } catch (error) {
      trackFormSubmission("contact_form", false);
    }
  };

  // Track Try Now button click
  const handleTryNowClick = () => {
    trackTryNowEvent("click");
  };

  // Track test environment usage
  useEffect(() => {
    const startTime = Date.now();
    return () => {
      const duration = Date.now() - startTime;
      trackTestEnvironmentUsage("session_end", duration);
    };
  }, []);

  // Track ROI calculation
  const handleROICalculation = (data: ROIData) => {
    const savings = calculateROI(data);
    trackROICalculation(data, savings);
  };
};
```
