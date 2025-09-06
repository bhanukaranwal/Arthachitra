// Mock lightweight-charts for testing

const mockSeries = {
  setData: jest.fn(),
  update: jest.fn(),
  applyOptions: jest.fn(),
};

const mockChart = {
  addCandlestickSeries: jest.fn(() => mockSeries),
  addLineSeries: jest.fn(() => mockSeries),
  addHistogramSeries: jest.fn(() => mockSeries),
  remove: jest.fn(),
  resize: jest.fn(),
  applyOptions: jest.fn(),
  timeScale: () => ({
    fitContent: jest.fn(),
    setVisibleRange: jest.fn(),
  }),
  priceScale: () => ({
    applyOptions: jest.fn(),
  }),
};

module.exports = {
  createChart: jest.fn(() => mockChart),
  LineStyle: {
    Solid: 0,
    Dotted: 1,
    Dashed: 2,
  },
  CrosshairMode: {
    Normal: 0,
    Magnet: 1,
  },
};
