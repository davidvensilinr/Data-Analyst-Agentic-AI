describe('Full Data Analyst Workflow', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000')
  })

  it('completes the landing page', () => {
    cy.contains('Autonomous Data Analyst').should('be.visible')
    cy.contains('Get Started').should('be.visible').click()
    cy.url().should('include', '/projects')
  })

  it('creates a new project and selects dataset', () => {
    cy.visit('http://localhost:3000/projects')
    cy.contains('New Project').click()
    cy.get('input[placeholder="Project name"]').type('Test Analysis')
    cy.contains('Create').click()
    cy.contains('Upload Dataset').should('be.visible')
  })

  it('uploads a CSV file', () => {
    const fileName = 'sample.csv'
    cy.visit('http://localhost:3000/projects/demo/upload')
    
    cy.get('input[type="file"]').selectFile({
      contents: Cypress.Buffer.from('Name,Age,City\nJohn,30,NYC\nJane,25,LA'),
      fileName: fileName,
      mimeType: 'text/csv',
    })

    cy.contains('sample.csv').should('be.visible')
  })

  it('displays data profile after upload', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/profile')
    cy.contains('Data Profiling').should('be.visible')
    cy.contains('Quality Score').should('be.visible')
  })

  it('opens cleaning editor', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/cleaning')
    cy.contains('Data Cleaning').should('be.visible')
    cy.get('[data-testid="cleaning-step"]').should('have.length.greaterThan', 0)
  })

  it('submits a query and views results', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/query')
    cy.get('textarea[placeholder*="question"]').type('What is the average age?')
    cy.contains('Run Analysis').click()
    cy.contains('Results').should('be.visible')
  })

  it('exports query results', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/query')
    cy.contains('Export Results').should('be.visible').click()
  })
})

describe('Data Profiling Dashboard', () => {
  it('displays column statistics', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/profile')
    cy.contains('Columns').should('be.visible')
    cy.get('[data-testid="column-card"]').should('have.length.greaterThan', 0)
  })

  it('shows data quality score', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/profile')
    cy.contains('Quality Score').should('be.visible')
  })

  it('displays histograms', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/profile')
    cy.get('[data-testid="histogram"]').should('exist')
  })
})

describe('Agent Trace Visualizer', () => {
  it('displays step execution trace', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/query')
    cy.get('textarea').type('Analyze sales trends')
    cy.contains('Run Analysis').click()
    cy.contains('Step Trace', { timeout: 5000 }).should('be.visible')
  })

  it('expands step details', () => {
    cy.visit('http://localhost:3000/projects/demo/datasets/demo-dataset-1/query')
    cy.contains('Run Analysis').click()
    cy.get('[data-testid="step-item"]').first().click()
    cy.contains('Prompt').should('be.visible')
  })
})
