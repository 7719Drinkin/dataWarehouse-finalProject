"""
数据治理服务
"""
import json
from typing import Dict, Any, List
from collections import Counter
import hashlib

class GovernanceService:
    """数据治理和溯源服务"""

    @staticmethod
    def calculate_data_quality_metrics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算数据质量指标"""
        if not data:
            return {
                'total_records': 0,
                'completeness': 0,
                'uniqueness': 0,
                'validity': 0
            }

        total_records = len(data)

        # 完整性检查 - 计算非空字段的比例
        completeness_scores = {}
        for record in data:
            for key, value in record.items():
                if key not in completeness_scores:
                    completeness_scores[key] = 0
                if value is not None and value != '':
                    completeness_scores[key] += 1

        completeness = {
            field: score / total_records
            for field, score in completeness_scores.items()
        }

        # 唯一性检查 - 计算唯一记录的比例
        unique_records = set()
        for record in data:
            # 创建记录的签名用于去重
            record_str = json.dumps(record, sort_keys=True, default=str)
            record_hash = hashlib.md5(record_str.encode()).hexdigest()
            unique_records.add(record_hash)

        uniqueness = len(unique_records) / total_records

        # 有效性检查 - 基本的数据类型和范围检查
        validity_issues = 0
        for record in data:
            # 检查评分是否在合理范围内
            score = record.get('score') or record.get('avg_score')
            if score is not None:
                try:
                    score_val = float(score)
                    if not (0 <= score_val <= 5):
                        validity_issues += 1
                except (ValueError, TypeError):
                    validity_issues += 1

            # 检查日期格式
            date_fields = ['release_date', 'review_time']
            for date_field in date_fields:
                date_val = record.get(date_field)
                if date_val and isinstance(date_val, str):
                    # 简单日期格式检查
                    if not any(fmt in date_val for fmt in ['-', '/', '.']):
                        validity_issues += 1

        validity = 1 - (validity_issues / total_records)

        return {
            'total_records': total_records,
            'completeness': {
                'overall': sum(completeness.values()) / len(completeness) if completeness else 0,
                'by_field': completeness
            },
            'uniqueness': uniqueness,
            'validity': validity,
            'quality_score': (sum(completeness.values()) / len(completeness) + uniqueness + validity) / 3 if completeness else 0
        }

    @staticmethod
    def generate_data_lineage_report(source_stats: Dict[str, Any]) -> Dict[str, Any]:
        """生成数据血缘报告"""
        return {
            'data_flow': {
                'raw_data_sources': ['snap_movies.txt', 'amazon_html_pages'],
                'processing_steps': [
                    'Data extraction from multiple sources',
                    'ETL transformation and cleaning',
                    'Data loading to Hive (primary)',
                    'Data synchronization to OpenGauss and Neo4j'
                ],
                'target_systems': ['Hive', 'OpenGauss', 'Neo4j']
            },
            'lineage_stats': source_stats,
            'data_quality_gates': [
                'Movie ID uniqueness validation',
                'Non-movie data filtering',
                'Field format standardization',
                'Reference data consistency checks'
            ]
        }

    @staticmethod
    def analyze_source_distribution(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析数据来源分布"""
        source_counts = Counter()
        source_file_counts = Counter()

        for record in data:
            source = record.get('source', 'unknown')
            source_file = record.get('source_file', 'unknown')

            source_counts[source] += 1
            source_file_counts[source_file] += 1

        return {
            'source_distribution': dict(source_counts),
            'source_file_distribution': dict(source_file_counts),
            'total_sources': len(source_counts),
            'total_source_files': len(source_file_counts)
        }

    @staticmethod
    def detect_data_anomalies(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检测数据异常"""
        anomalies = {
            'missing_critical_fields': [],
            'invalid_ratings': [],
            'duplicate_records': [],
            'inconsistent_dates': []
        }

        seen_records = set()

        for i, record in enumerate(data):
            # 检查关键字段缺失
            critical_fields = ['movie_id', 'title']
            missing_fields = [field for field in critical_fields if not record.get(field)]
            if missing_fields:
                anomalies['missing_critical_fields'].append({
                    'record_index': i,
                    'missing_fields': missing_fields
                })

            # 检查评分异常
            score = record.get('score') or record.get('avg_score')
            if score is not None:
                try:
                    score_val = float(score)
                    if not (0 <= score_val <= 5):
                        anomalies['invalid_ratings'].append({
                            'record_index': i,
                            'score': score_val
                        })
                except (ValueError, TypeError):
                    anomalies['invalid_ratings'].append({
                        'record_index': i,
                        'score': score
                    })

            # 检查重复记录
            record_str = json.dumps(record, sort_keys=True, default=str)
            record_hash = hashlib.md5(record_str.encode()).hexdigest()
            if record_hash in seen_records:
                anomalies['duplicate_records'].append({
                    'record_index': i,
                    'duplicate_hash': record_hash
                })
            else:
                seen_records.add(record_hash)

            # 检查日期一致性
            release_date = record.get('release_date')
            review_time = record.get('review_time')
            if release_date and review_time:
                try:
                    # 简单检查：评论时间不应早于发布日期
                    if isinstance(release_date, str) and isinstance(review_time, str):
                        release_year = int(release_date.split('-')[0]) if '-' in release_date else None
                        review_year = int(review_time.split('-')[0]) if '-' in review_time else None

                        if release_year and review_year and review_year < release_year:
                            anomalies['inconsistent_dates'].append({
                                'record_index': i,
                                'release_date': release_date,
                                'review_time': review_time
                            })
                except (ValueError, IndexError):
                    pass

        return {
            'total_anomalies': sum(len(anomaly_list) for anomaly_list in anomalies.values()),
            'anomalies_by_type': {k: len(v) for k, v in anomalies.items()},
            'detailed_anomalies': anomalies
        }

    @staticmethod
    def generate_quality_report(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成完整的数据质量报告"""
        quality_metrics = GovernanceService.calculate_data_quality_metrics(data)
        source_analysis = GovernanceService.analyze_source_distribution(data)
        anomaly_detection = GovernanceService.detect_data_anomalies(data)

        return {
            'quality_metrics': quality_metrics,
            'source_analysis': source_analysis,
            'anomaly_detection': anomaly_detection,
            'recommendations': GovernanceService._generate_recommendations(
                quality_metrics, anomaly_detection
            ),
            'generated_at': 'current_timestamp'
        }

    @staticmethod
    def _generate_recommendations(quality_metrics: Dict[str, Any], anomalies: Dict[str, Any]) -> List[str]:
        """生成数据质量改进建议"""
        recommendations = []

        # 基于质量指标的建议
        if quality_metrics['completeness']['overall'] < 0.8:
            recommendations.append("Improve data completeness by implementing mandatory field validation")

        if quality_metrics['uniqueness'] < 0.95:
            recommendations.append("Implement stronger deduplication logic to improve data uniqueness")

        if quality_metrics['validity'] < 0.9:
            recommendations.append("Add data type validation and range checks for better data validity")

        # 基于异常检测的建议
        if anomalies['anomalies_by_type']['missing_critical_fields'] > 0:
            recommendations.append("Review ETL process to ensure critical fields are always populated")

        if anomalies['anomalies_by_type']['invalid_ratings'] > 0:
            recommendations.append("Implement rating validation in data ingestion pipeline")

        if anomalies['anomalies_by_type']['duplicate_records'] > 0:
            recommendations.append("Enhance deduplication strategy using composite keys")

        if anomalies['anomalies_by_type']['inconsistent_dates'] > 0:
            recommendations.append("Add date consistency validation in data transformation")

        return recommendations
