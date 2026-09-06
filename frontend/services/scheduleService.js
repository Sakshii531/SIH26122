import { MOCK_PROJECTS, MOCK_PROJECT_STATS } from './mock/mockProjects.js';
import { MOCK_WBS_TREE, MOCK_ALL_L6_ACTIVITIES } from './mock/mockSchedules.js';

export const scheduleService = {
  /**
   * Get list of all infrastructure projects
   */
  async getProjects() {
    return MOCK_PROJECTS;
  },

  /**
   * Get active project details by ID
   */
  async getProjectById(id) {
    return MOCK_PROJECTS.find(p => p.id === id) || MOCK_PROJECTS[0];
  },

  /**
   * Get WBS tree for active project
   */
  async getWBSTree(projectId) {
    return MOCK_WBS_TREE;
  },

  /**
   * Get flat list of all L6 activities for filtering and searching
   */
  async getL6Activities(projectId, filters = {}) {
    let list = [...MOCK_ALL_L6_ACTIVITIES];
    if (filters.discipline) {
      list = list.filter(a => a.discipline.toLowerCase() === filters.discipline.toLowerCase());
    }
    if (filters.status) {
      list = list.filter(a => a.status.toLowerCase() === filters.status.toLowerCase());
    }
    if (filters.query) {
      const q = filters.query.toLowerCase();
      list = list.filter(a => a.name.toLowerCase().includes(q) || a.code.toLowerCase().includes(q) || a.wbsPath.toLowerCase().includes(q));
    }
    return list;
  },

  /**
   * Get high-level summary KPIs
   */
  async getProjectStats() {
    return MOCK_PROJECT_STATS;
  }
};
