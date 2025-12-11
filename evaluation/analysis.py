"""
Comprehensive Analysis of Model Evaluation Results
"""

import json
import os
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class ResultsAnalyzer:
    """Analyze and visualize evaluation results"""
    
    def __init__(self, comparison_file: str):
        """Load comparison results"""
        with open(comparison_file, 'r') as f:
            self.data = json.load(f)
        
        self.mistral = self.data['mistral']
        self.llama = self.data['llama']
        self.detailed = self.data['detailed_comparison']
        
        # Create output directory
        self.output_dir = Path(comparison_file).parent / "analysis"
        self.output_dir.mkdir(exist_ok=True)
    
    def print_summary(self):
        """Print comprehensive text summary"""
        print("SJSU VIRTUAL ASSISTANT - MODEL COMPARISON ANALYSIS")
        print()
        
        print("OVERALL PERFORMANCE METRICS")
        print(f"{'Metric':<30} {'Mistral-7B':>20} {'Llama-3.2-11B':>20}")
        print(f"{'Average Response Time':<30} {self.mistral['averages']['response_time']:>18.2f}s {self.llama['averages']['response_time']:>18.2f}s")
        print(f"{'Completeness Score':<30} {self.mistral['averages']['completeness_score']:>20.2f} {self.llama['averages']['completeness_score']:>20.2f}")
        print(f"{'Relevance Score':<30} {self.mistral['averages']['relevance_score']:>20.2f} {self.llama['averages']['relevance_score']:>20.2f}")
        print(f"{'Avg Response Length (words)':<30} {self.mistral['averages']['response_length_words']:>20.0f} {self.llama['averages']['response_length_words']:>20.0f}")
        print(f"{'Injection Defense Rate':<30} {self.mistral['security']['injection_defense_rate']:>20.1%} {self.llama['security']['injection_defense_rate']:>20.1%}")
        print()
        
        print("WINNERS")
        speed_diff = abs(self.mistral['averages']['response_time'] - self.llama['averages']['response_time'])
        speed_pct = (speed_diff / max(self.mistral['averages']['response_time'], self.llama['averages']['response_time'])) * 100
        print(f"Speed: Llama-3.2-11B ({speed_pct:.1f}% faster)")
        
        comp_diff = abs(self.mistral['averages']['completeness_score'] - self.llama['averages']['completeness_score'])
        comp_pct = (comp_diff / max(self.mistral['averages']['completeness_score'], 0.01)) * 100
        print(f"Completeness: Mistral-7B ({comp_pct:.1f}% higher score)")
        
        rel_diff = abs(self.mistral['averages']['relevance_score'] - self.llama['averages']['relevance_score'])
        rel_pct = (rel_diff / max(self.mistral['averages']['relevance_score'], 0.01)) * 100
        print(f"Relevance: Mistral-7B ({rel_pct:.1f}% higher score)")
        print()
        
        print("PERFORMANCE BY CATEGORY")
        
        # Get all categories
        categories = set(self.mistral['by_category'].keys()) | set(self.llama['by_category'].keys())
        
        for cat in sorted(categories):
            if cat in self.mistral['by_category'] and cat in self.llama['by_category']:
                m_data = self.mistral['by_category'][cat]
                l_data = self.llama['by_category'][cat]
                
                print(f"\n{cat.upper().replace('_', ' ')}")
                print(f"  Mistral: {m_data['avg_time']:.1f}s | Completeness: {m_data['avg_completeness']:.2f}")
                print(f"  Llama: {l_data['avg_time']:.1f}s | Completeness: {l_data['avg_completeness']:.2f}")
        
        print()
        print("KEY INSIGHTS")
        
        # Analyze patterns
        insights = self._generate_insights()
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        print()
    
    def _generate_insights(self) -> List[str]:
        """Generate key insights from the data"""
        insights = []
        
        # Speed analysis
        if self.llama['averages']['response_time'] < self.mistral['averages']['response_time']:
            insights.append("Llama-3.2-11B is consistently faster despite being a larger model (11B vs 7B parameters)")
        
        # Completeness analysis
        if self.mistral['averages']['completeness_score'] > self.llama['averages']['completeness_score']:
            insights.append("Mistral-7B provides more complete answers, better covering expected information")
        
        # Timeout analysis
        mistral_timeouts = sum(1 for item in self.detailed if item['mistral']['completeness'] == 0.0)
        llama_timeouts = sum(1 for item in self.detailed if item['llama']['completeness'] == 0.0)
        
        if mistral_timeouts > 5 or llama_timeouts > 5:
            insights.append(f"High iteration timeout rate detected (Mistral: {mistral_timeouts}/20, Llama: {llama_timeouts}/20) - suggests agent needs tuning")
        
        # Security
        if self.mistral['security']['injection_defense_rate'] == 1.0 and self.llama['security']['injection_defense_rate'] == 1.0:
            insights.append("Both models successfully defended against prompt injection attacks (100% defense rate)")
        
        # Category strengths
        best_mistral = max(self.mistral['by_category'].items(), key=lambda x: x[1]['avg_completeness'])
        best_llama = max(self.llama['by_category'].items(), key=lambda x: x[1]['avg_completeness'])
        
        insights.append(f"Mistral excels at {best_mistral[0].replace('_', ' ')} queries (completeness: {best_mistral[1]['avg_completeness']:.2f})")
        insights.append(f"Llama excels at {best_llama[0].replace('_', ' ')} queries (completeness: {best_llama[1]['avg_completeness']:.2f})")
        
        # Response length
        if self.mistral['averages']['response_length_words'] > self.llama['averages']['response_length_words'] * 1.5:
            insights.append("Mistral generates significantly longer responses (potential verbosity issue)")
        
        return insights
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        print("\nCreating visualizations...")
        
        # 1. Overall metrics comparison
        self._plot_overall_metrics()
        
        # 2. Response time by category
        self._plot_time_by_category()
        
        # 3. Completeness by category
        self._plot_completeness_by_category()
        
        # 4. Query-by-query comparison
        self._plot_query_comparison()
        
        # 5. Speed vs Completeness scatter
        self._plot_speed_vs_completeness()
        
        print(f"All visualizations saved to: {self.output_dir}")
    
    def _plot_overall_metrics(self):
        """Plot overall metric comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Overall Model Comparison', fontsize=16, fontweight='bold')
        
        models = ['Mistral-7B', 'Llama-3.2-11B']
        colors = ['#FF6B6B', '#4ECDC4']
        
        # Response time
        times = [self.mistral['averages']['response_time'], self.llama['averages']['response_time']]
        axes[0, 0].bar(models, times, color=colors, alpha=0.7, edgecolor='black')
        axes[0, 0].set_ylabel('Seconds')
        axes[0, 0].set_title('Average Response Time (Lower is Better)')
        axes[0, 0].set_ylim(0, max(times) * 1.2)
        for i, v in enumerate(times):
            axes[0, 0].text(i, v + 1, f'{v:.1f}s', ha='center', fontweight='bold')
        
        # Completeness
        completeness = [self.mistral['averages']['completeness_score'], self.llama['averages']['completeness_score']]
        axes[0, 1].bar(models, completeness, color=colors, alpha=0.7, edgecolor='black')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].set_title('Average Completeness Score (Higher is Better)')
        axes[0, 1].set_ylim(0, 1)
        for i, v in enumerate(completeness):
            axes[0, 1].text(i, v + 0.02, f'{v:.2f}', ha='center', fontweight='bold')
        
        # Relevance
        relevance = [self.mistral['averages']['relevance_score'], self.llama['averages']['relevance_score']]
        axes[1, 0].bar(models, relevance, color=colors, alpha=0.7, edgecolor='black')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].set_title('Average Relevance Score (Higher is Better)')
        axes[1, 0].set_ylim(0, 1)
        for i, v in enumerate(relevance):
            axes[1, 0].text(i, v + 0.02, f'{v:.2f}', ha='center', fontweight='bold')
        
        # Response length
        lengths = [self.mistral['averages']['response_length_words'], self.llama['averages']['response_length_words']]
        axes[1, 1].bar(models, lengths, color=colors, alpha=0.7, edgecolor='black')
        axes[1, 1].set_ylabel('Words')
        axes[1, 1].set_title('Average Response Length')
        for i, v in enumerate(lengths):
            axes[1, 1].text(i, v + 1, f'{int(v)}', ha='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '1_overall_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_time_by_category(self):
        """Plot response time by category"""
        categories = sorted(set(self.mistral['by_category'].keys()) & set(self.llama['by_category'].keys()))
        
        mistral_times = [self.mistral['by_category'][cat]['avg_time'] for cat in categories]
        llama_times = [self.llama['by_category'][cat]['avg_time'] for cat in categories]
        
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, mistral_times, width, label='Mistral-7B', color='#FF6B6B', alpha=0.7)
        ax.bar(x + width/2, llama_times, width, label='Llama-3.2-11B', color='#4ECDC4', alpha=0.7)
        
        ax.set_xlabel('Category')
        ax.set_ylabel('Average Response Time (seconds)')
        ax.set_title('Response Time by Query Category')
        ax.set_xticks(x)
        ax.set_xticklabels([cat.replace('_', '\n') for cat in categories])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '2_time_by_category.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_completeness_by_category(self):
        """Plot completeness by category"""
        categories = sorted(set(self.mistral['by_category'].keys()) & set(self.llama['by_category'].keys()))
        
        mistral_comp = [self.mistral['by_category'][cat]['avg_completeness'] for cat in categories]
        llama_comp = [self.llama['by_category'][cat]['avg_completeness'] for cat in categories]
        
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x - width/2, mistral_comp, width, label='Mistral-7B', color='#FF6B6B', alpha=0.7)
        ax.bar(x + width/2, llama_comp, width, label='Llama-3.2-11B', color='#4ECDC4', alpha=0.7)
        
        ax.set_xlabel('Category')
        ax.set_ylabel('Average Completeness Score')
        ax.set_title('Completeness Score by Query Category')
        ax.set_xticks(x)
        ax.set_xticklabels([cat.replace('_', '\n') for cat in categories])
        ax.legend()
        ax.set_ylim(0, 1)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '3_completeness_by_category.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_query_comparison(self):
        """Plot query-by-query comparison"""
        query_ids = [item['query_id'] for item in self.detailed]
        mistral_times = [item['mistral']['time'] for item in self.detailed]
        llama_times = [item['llama']['time'] for item in self.detailed]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Response times
        x = np.arange(len(query_ids))
        width = 0.35
        ax1.bar(x - width/2, mistral_times, width, label='Mistral-7B', color='#FF6B6B', alpha=0.7)
        ax1.bar(x + width/2, llama_times, width, label='Llama-3.2-11B', color='#4ECDC4', alpha=0.7)
        ax1.set_xlabel('Query ID')
        ax1.set_ylabel('Response Time (seconds)')
        ax1.set_title('Response Time per Query')
        ax1.set_xticks(x)
        ax1.set_xticklabels(query_ids, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Completeness scores
        mistral_comp = [item['mistral']['completeness'] for item in self.detailed]
        llama_comp = [item['llama']['completeness'] for item in self.detailed]
        
        ax2.bar(x - width/2, mistral_comp, width, label='Mistral-7B', color='#FF6B6B', alpha=0.7)
        ax2.bar(x + width/2, llama_comp, width, label='Llama-3.2-11B', color='#4ECDC4', alpha=0.7)
        ax2.set_xlabel('Query ID')
        ax2.set_ylabel('Completeness Score')
        ax2.set_title('Completeness Score per Query')
        ax2.set_xticks(x)
        ax2.set_xticklabels(query_ids, rotation=45, ha='right')
        ax2.legend()
        ax2.set_ylim(0, 1)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '4_query_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_speed_vs_completeness(self):
        """Plot speed vs completeness scatter"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Mistral data points
        mistral_times = [item['mistral']['time'] for item in self.detailed]
        mistral_comp = [item['mistral']['completeness'] for item in self.detailed]
        ax.scatter(mistral_times, mistral_comp, s=100, alpha=0.6, color='#FF6B6B', label='Mistral-7B', edgecolors='black')
        
        # Llama data points
        llama_times = [item['llama']['time'] for item in self.detailed]
        llama_comp = [item['llama']['completeness'] for item in self.detailed]
        ax.scatter(llama_times, llama_comp, s=100, alpha=0.6, color='#4ECDC4', label='Llama-3.2-11B', edgecolors='black')
        
        ax.set_xlabel('Response Time (seconds)')
        ax.set_ylabel('Completeness Score')
        ax.set_title('Speed vs Quality Trade-off')
        ax.legend()
        ax.grid(alpha=0.3)
        ax.set_ylim(-0.05, 1.05)
        
        # Add ideal region (fast + complete)
        ax.axhline(y=0.7, color='green', linestyle='--', alpha=0.3, label='Good completeness threshold')
        ax.axvline(x=60, color='orange', linestyle='--', alpha=0.3, label='Fast response threshold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '5_speed_vs_completeness.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Speed recommendation
        if self.llama['averages']['response_time'] < self.mistral['averages']['response_time'] * 0.7:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Performance',
                'recommendation': 'Use Llama-3.2-11B for production - significantly faster response times',
                'rationale': f"Llama is {((self.mistral['averages']['response_time'] / self.llama['averages']['response_time']) - 1) * 100:.1f}% faster on average"
            })
        
        # Quality recommendation
        if self.mistral['averages']['completeness_score'] > self.llama['averages']['completeness_score'] + 0.1:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Quality',
                'recommendation': 'Consider Mistral-7B for applications requiring high completeness',
                'rationale': f"Mistral provides {((self.mistral['averages']['completeness_score'] / self.llama['averages']['completeness_score']) - 1) * 100:.1f}% better completeness"
            })
        
        # Timeout recommendation
        mistral_timeouts = sum(1 for item in self.detailed if item['mistral']['completeness'] == 0.0)
        llama_timeouts = sum(1 for item in self.detailed if item['llama']['completeness'] == 0.0)
        
        if mistral_timeouts > 5:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Reliability',
                'recommendation': 'Mistral-7B has high timeout rate - increase max iterations or use Llama',
                'rationale': f"Mistral timed out on {mistral_timeouts}/{len(self.detailed)} queries ({mistral_timeouts/len(self.detailed)*100:.1f}%)"
            })
        
        return recommendations
    
    def print_recommendations(self):
        """Print recommendations"""
        print("\nRECOMMENDATIONS")
        
        recommendations = self.generate_recommendations()
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['category']}")
            print(f"   {rec['recommendation']}")
            print(f"   Rationale: {rec['rationale']}")
        
    def save_report(self):
        """Save comprehensive text report"""
        report_path = self.output_dir / "analysis_report.txt"
        
        import sys
        from io import StringIO
        
        # Capture print output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        self.print_summary()
        self.print_recommendations()
        
        report_content = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Save to file
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"\nAnalysis report saved to: {report_path}")


def main():
    """Main analysis function"""
    # Look for comparison files
    results_dir = Path("evaluation/results")
    
    if not results_dir.exists():
        print("No comparison files found in evaluation/results/")
        return
    
    comparison_files = list(results_dir.glob("*comparison*.json"))
    
    if not comparison_files:
        print("No comparison files found in evaluation/results/")
        return
    
    # Use the most recent comparison file
    comparison_file = sorted(comparison_files)[-1]
    print(f"Analyzing: {comparison_file}")
    
    # Create analyzer
    analyzer = ResultsAnalyzer(str(comparison_file))
    
    # Generate analysis
    analyzer.print_summary()
    analyzer.create_visualizations()
    analyzer.print_recommendations()
    analyzer.save_report()
    
    print("\nAnalysis complete!")
    print(f"Results saved to: {analyzer.output_dir}")


if __name__ == "__main__":
    main()
