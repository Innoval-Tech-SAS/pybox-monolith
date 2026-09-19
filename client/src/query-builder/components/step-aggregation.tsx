import { StepAggregation as SharedStepAggregation } from "@/ui/components/aggregation/step-aggregation";
import { useEntityFields } from "@/query-builder/hooks/use-entity-fields";
import type { StepAggregationProps } from "@/query-builder/types/step-aggregation-props";

export const StepAggregation: React.FC<StepAggregationProps> = ({ state, update, config }) => (
  <SharedStepAggregation
    state={state}
    onUpdate={update}
    useFields={useEntityFields}
    copy={{
      entityNoun: config.copy.entityNoun,
      toggleHelpExample: config.copy.toggleHelpExample,
      havingExampleMetric: config.copy.havingExampleMetric,
    }}
  />
);
