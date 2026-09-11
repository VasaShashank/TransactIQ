import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { GraphData } from '../types';

interface GraphViewerProps {
  data: GraphData;
  onSelectAccount?: (account_id: string) => void;
}

export const GraphViewer: React.FC<GraphViewerProps> = ({ data, onSelectAccount }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const elements: cytoscape.ElementDefinition[] = [];

    data.nodes.forEach((n) => {
      elements.push({
        group: 'nodes',
        data: {
          id: n.data.id,
          label: n.data.label,
          node_type: n.data.node_type,
          is_target: n.data.is_target ? 'true' : 'false'
        }
      });
    });

    data.edges.forEach((e) => {
      elements.push({
        group: 'edges',
        data: {
          id: e.data.id,
          source: e.data.source,
          target: e.data.target,
          amount: e.data.amount,
          type: e.data.type,
          is_fraud: e.data.is_fraud
        }
      });
    });

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#3B82F6',
            'label': 'data(id)',
            'color': '#F8FAFC',
            'font-size': '10px',
            'font-weight': 'bold',
            'text-valign': 'bottom',
            'text-margin-y': 5,
            'width': 36,
            'height': 36,
            'border-width': 2,
            'border-color': 'rgba(255, 255, 255, 0.3)'
          }
        },
        {
          selector: 'node[is_target = "true"]',
          style: {
            'background-color': '#EC4899',
            'width': 48,
            'height': 48,
            'border-width': 4,
            'border-color': '#FFF'
          }
        },
        {
          selector: 'node[node_type = "MERCHANT"]',
          style: {
            'shape': 'diamond',
            'background-color': '#10B981'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.7
          }
        },
        {
          selector: 'edge[is_fraud = 1]',
          style: {
            'line-color': '#EF4444',
            'target-arrow-color': '#EF4444',
            'width': 4,
            'opacity': 1.0
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 500,
        fit: true,
        padding: 40
      }
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      if (onSelectAccount) {
        onSelectAccount(node.id());
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [data, onSelectAccount]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '480px' }}>
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: '100%',
          borderRadius: '10px',
          background: 'rgba(9, 13, 22, 0.8)',
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}
      />
      <div style={{
        position: 'absolute',
        top: 12,
        right: 12,
        background: 'rgba(15, 23, 42, 0.9)',
        padding: '10px 14px',
        borderRadius: '8px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        fontSize: '0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <div style={{ fontWeight: 600, color: '#94A3B8', marginBottom: '2px' }}>Graph Legend</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#EC4899' }} /> Target Account
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#3B82F6' }} /> Customer Account
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '12px', height: '12px', transform: 'rotate(45deg)', background: '#10B981' }} /> Merchant Node
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '16px', height: '3px', background: '#EF4444' }} /> Fraudulent Txn Edge
        </div>
      </div>
    </div>
  );
};
