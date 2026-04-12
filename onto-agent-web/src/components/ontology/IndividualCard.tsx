import type { Individual } from "@/services/ontologyApi";

interface IndividualCardProps {
  individual: Individual;
  dataProperties: Array<{
    id: string;
    name: string;
    displayName?: string;
    rangeType?: string;
  }>;
  objectProperties: Array<{
    id: string;
    name: string;
    displayName?: string;
  }>;
  onClick?: (individual: Individual) => void;
  onEdit?: (individual: Individual) => void;
  onDelete?: (id: string) => void;
  onNavigateToIndividual?: (individualId: string) => void;
}

export function IndividualCard({
  individual,
  dataProperties,
  objectProperties,
  onClick,
  onEdit,
  onDelete,
  onNavigateToIndividual,
}: IndividualCardProps) {
  // 获取属性显示名称
  const getPropName = (propId: string) => {
    const prop = dataProperties.find((p) => p.id === propId || p.name === propId);
    return prop?.displayName || prop?.name || propId;
  };

  const getObjPropName = (propId: string) => {
    const prop = objectProperties.find((p) => p.id === propId || p.name === propId);
    return prop?.displayName || prop?.name || propId;
  };

  return (
    <div className="individual-card" onClick={() => onClick?.(individual)}>
      <div className="individual-card-header">
        <div className="individual-name">
          <span className="individual-icon">👤</span>
          <span className="individual-display">
            {individual.displayName || individual.name}
          </span>
          <span className="individual-id">({individual.name})</span>
        </div>
        <div className="individual-actions">
          {onEdit && (
            <button
              className="individual-edit"
              onClick={(e) => {
                e.stopPropagation();
                onEdit(individual);
              }}
            >
              编辑
            </button>
          )}
          {onDelete && (
            <button
              className="individual-delete"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(individual.id);
              }}
            >
              删除
            </button>
          )}
        </div>
      </div>

      <div className="individual-card-body">
        {/* 数据属性 */}
        {individual.dataPropertyAssertions &&
          individual.dataPropertyAssertions.length > 0 && (
            <div className="individual-section">
              <div className="section-label">数据属性</div>
              {individual.dataPropertyAssertions.map((assertion, idx) => (
                <div key={idx} className="individual-assertion">
                  <span className="assertion-prop">
                    {getPropName(assertion.propertyId)}:
                  </span>
                  <span className="assertion-value">
                    "{String(assertion.value)}"
                  </span>
                </div>
              ))}
            </div>
          )}

        {/* 对象属性 */}
        {individual.objectPropertyAssertions &&
          individual.objectPropertyAssertions.length > 0 && (
            <div className="individual-section">
              <div className="section-label">对象属性</div>
              {individual.objectPropertyAssertions.map((assertion, idx) => (
                <div key={idx} className="individual-assertion">
                  <span className="assertion-prop">
                    {getObjPropName(assertion.propertyId)}:
                  </span>
                  <span
                    className="assertion-target"
                    onClick={(e) => {
                      e.stopPropagation();
                      onNavigateToIndividual?.(assertion.targetIndividualId);
                    }}
                  >
                    👤 {assertion.targetIndividualId}
                  </span>
                </div>
              ))}
            </div>
          )}

        {/* 空状态 */}
        {(!individual.dataPropertyAssertions ||
          individual.dataPropertyAssertions.length === 0) &&
          (!individual.objectPropertyAssertions ||
            individual.objectPropertyAssertions.length === 0) && (
            <div className="individual-empty">暂无属性断言</div>
          )}
      </div>
    </div>
  );
}

export default IndividualCard;
