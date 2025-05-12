<?php
/**
 * Strength-Weakness Bar Chart Component
 * 
 * Displays the user's strengths and weaknesses as bar charts
 * 
 * Props:
 * - chartId: Unique ID for the chart
 * - data: Chart data with strengths and weaknesses
 */
?>

<div class="bg-white p-4 rounded-lg shadow-md">
    <h3 class="text-lg font-semibold mb-4">{{ $title ?? 'Strengths & Weaknesses' }}</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
            <h4 class="text-md font-medium text-green-700 mb-2">Strengths</h4>
            <canvas id="{{ $chartId }}_strengths"></canvas>
        </div>
        
        <div>
            <h4 class="text-md font-medium text-red-700 mb-2">Areas for Improvement</h4>
            <canvas id="{{ $chartId }}_weaknesses"></canvas>
        </div>
    </div>
    
    @push('scripts')
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const data = @json($data);
            
            // Strengths Chart
            if (data.strengths && data.strengths.labels.length > 0) {
                const strengthsCtx = document.getElementById('{{ $chartId }}_strengths').getContext('2d');
                new Chart(strengthsCtx, {
                    type: 'bar',
                    data: {
                        labels: data.strengths.labels,
                        datasets: [{
                            label: 'Score (%)',
                            data: data.strengths.data,
                            backgroundColor: 'rgba(72, 187, 120, 0.7)',
                            borderColor: 'rgb(72, 187, 120)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
            
            // Weaknesses Chart
            if (data.weaknesses && data.weaknesses.labels.length > 0) {
                const weaknessesCtx = document.getElementById('{{ $chartId }}_weaknesses').getContext('2d');
                new Chart(weaknessesCtx, {
                    type: 'bar',
                    data: {
                        labels: data.weaknesses.labels,
                        datasets: [{
                            label: 'Score (%)',
                            data: data.weaknesses.data,
                            backgroundColor: 'rgba(245, 101, 101, 0.7)',
                            borderColor: 'rgb(245, 101, 101)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
        });
    </script>
    @endpush
</div>