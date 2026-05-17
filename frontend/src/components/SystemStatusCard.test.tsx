import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { SystemStatusCard } from './SystemStatusCard';


describe('SystemStatusCard', () => {
  it('renders system health values', () => {
    render(
      <SystemStatusCard
        health={{
          status: 'ok',
          backend: 'ok',
          database: 'ok',
          app_name: 'Territory Growth Intelligence MAS',
          environment: 'test',
        }}
        isLoading={false}
        error=''
        onRefresh={() => undefined}
      />,
    );
    expect(screen.getByText(/territory growth intelligence mas/i)).toBeInTheDocument();
    expect(screen.getByText(/test/i)).toBeInTheDocument();
  });
});
