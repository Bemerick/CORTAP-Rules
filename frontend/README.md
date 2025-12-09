# FTA Comprehensive Review - Frontend

React + TypeScript frontend application for FTA Comprehensive Review Applicability Assessment and Level of Effort (LOE) Estimation.

## Features

- **Interactive Questionnaire**: Dynamic assessment questions with conditional logic
- **Project Management**: Create and manage multiple review projects
- **Real-time Assessment**: Instant calculation of applicable review areas
- **LOE Summary**: Visual breakdown of estimated hours by section
- **Excel Export**: Generate audit-ready workbooks from assessment results
- **Responsive Design**: Works on desktop and tablet devices

## Tech Stack

- **React 18**: UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **CSS Modules**: Scoped styling

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

The frontend expects the backend API to be running at `http://localhost:8000` by default. Update the API base URL in `src/services/api.ts` if needed.

## Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Application Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Questionnaire.tsx
│   │   ├── ApplicabilityResults.tsx
│   │   ├── LOESummary.tsx
│   │   └── ...
│   ├── pages/              # Page-level components
│   │   ├── ProjectsPage.tsx
│   │   ├── ProjectAssessmentPage.tsx
│   │   ├── ProjectResultsPage.tsx
│   │   └── LOESummaryPage.tsx
│   ├── services/           # API service layer
│   │   └── api.ts
│   ├── types/              # TypeScript type definitions
│   │   └── api.ts
│   ├── App.tsx             # Root component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── package.json
└── vite.config.ts         # Vite configuration
```

## Key Features

### 1. Project Assessment Workflow

1. **Create Project**: User creates a new project
2. **Answer Questions**: Complete the assessment questionnaire
3. **View Results**: See which review areas apply
4. **Review LOE**: Check estimated hours breakdown
5. **Export Workbook**: Download Excel file for audit work

### 2. Excel Workbook Export

The application can generate Excel workbooks with:
- One tab per applicable section
- Questions with sub-area IDs
- Indicators of Compliance
- Pre-formatted audit columns (Compliant, Non-Compliant, N/A, etc.)
- Proper chapter numbering

Access via "Generate Scoping Workbook" button on results page.

### 3. LOE Summary

Visual breakdown showing:
- Total estimated hours per section
- Number of applicable sub-areas
- Number of indicators of compliance
- Average confidence scores

## API Integration

The frontend communicates with the FastAPI backend through the `ApiService` class in `src/services/api.ts`.

### Main API Methods:

- `getQuestions()` - Fetch assessment questions
- `createProject()` - Create new project
- `submitProjectAnswers()` - Submit answers and calculate applicability
- `getProjectApplicableSubAreas()` - Get assessment results
- `getProjectLOESummary()` - Get LOE breakdown
- `exportProjectWorkbook()` - Download Excel workbook

## Development

### Adding New Features

1. Create component in `src/components/`
2. Add types to `src/types/api.ts`
3. Add API methods to `src/services/api.ts`
4. Update routing in `App.tsx`

### Code Quality

```bash
# Run linter
npm run lint

# Type check
npx tsc --noEmit
```

## Deployment

### Environment Variables

For production, configure:
- API base URL (if different from default)
- Any feature flags

### Build Process

```bash
npm run build
```

Deploy the `dist/` folder to your hosting platform (Netlify, Vercel, etc.).

### CORS Configuration

Ensure the backend's `ALLOWED_ORIGINS` environment variable includes your frontend URL.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Proprietary - FTA Comprehensive Review Application
