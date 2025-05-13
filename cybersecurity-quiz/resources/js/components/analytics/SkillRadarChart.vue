<template>
  <div class="radar-chart-container">
    <h3 class="chart-title">{{ title }}</h3>
    <canvas ref="radarChart"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'

export default {
  name: 'SkillRadarChart',
  props: {
    title: {
      type: String,
      default: 'Skill Proficiency'
    },
    skillData: {
      type: Array,
      required: true,
      // Expected format: 
      // [{ name: 'Network Security', value: 75, average: 65 }, ...]
    }
  },
  data() {
    return {
      chart: null
    }
  },
  watch: {
    skillData: {
      handler() {
        this.renderChart()
      },
      deep: true
    }
  },
  mounted() {
    this.renderChart()
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.destroy()
    }
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.radarChart.getContext('2d')
      
      // Prepare data for chart
      const labels = this.skillData.map(item => item.name)
      const userValues = this.skillData.map(item => item.value)
      const averageValues = this.skillData.map(item => item.average)
      
      // Destroy previous chart if it exists
      if (this.chart) {
        this.chart.destroy()
      }
      
      // Create chart
      this.chart = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Your Skills',
              data: userValues,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
              pointRadius: 4
            },
            {
              label: 'Peer Average',
              data: averageValues,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              pointBackgroundColor: 'rgba(255, 99, 132, 1)',
              pointRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              min: 0,
              max: 100,
              ticks: {
                stepSize: 20
              }
            }
          },
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.radar-chart-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  height: 400px;
}

.chart-title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 16px;
  text-align: center;
}
</style>