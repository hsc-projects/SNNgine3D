import numpy as np


def segment_intersection2d(seg0: np.ndarray, seg1: np.ndarray):
    """
    Computer Graphics by F.S. Hill, Chapter 4, Section 6
    """
    if seg0.shape != (2, 2) or seg1.shape != (2, 2):
        raise ValueError

    seg0 = seg0.astype(np.float64)
    seg1 = seg1.astype(np.float64)

    vec_ab = seg0[1] - seg0[0]
    vec_cd = seg1[1] - seg1[0]

    vec_cd_perp = np.array([-vec_cd[1], vec_cd[0]])

    return seg0[0] + vec_ab * (np.dot(vec_cd_perp, seg1[0] - seg0[0])
                               / np.dot(vec_cd_perp, vec_ab))


if __name__ == "__main__":
    ab = np.array([[1, 1], [3, 1]])
    cd = np.array([[0, 2], [0, 4]])
    print(segment_intersection2d(ab, cd))
    assert np.sum(segment_intersection2d(ab, cd) - np.array([0, 1])) == 0

    ab = np.array([[1, 1], [3, 3]])
    cd = np.array([[1, 3], [3, 1]])
    print(segment_intersection2d(ab, cd))
    assert np.sum(segment_intersection2d(ab, cd) - np.array([2, 2])) == 0


